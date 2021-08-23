using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using checker.net;
using checker.rnd;
using checker.utils;

namespace checker.svghost
{
	internal class SvghostChecker : IChecker
	{
		public Task<string> Info() => Task.FromResult("vulns: 1");

		public async Task Check(string host)
		{
			var client = new AsyncHttpClient(GetBaseUri(host), true);

			var result = await client.DoRequestAsync(HttpMethod.Get, "/", null, null, NetworkOpTimeout, MaxHttpBodySize).ConfigureAwait(false);
			if(result.StatusCode != HttpStatusCode.OK)
				throw new CheckerException(result.StatusCode.ToExitCode(), "get / failed");

			await RndUtil.RndDelay(MaxDelay).ConfigureAwait(false);

			result = await client.DoRequestAsync(HttpMethod.Get, ApiMe, null, null, NetworkOpTimeout, MaxHttpBodySize).ConfigureAwait(false);
			if(result.StatusCode != HttpStatusCode.OK)
				throw new CheckerException(result.StatusCode.ToExitCode(), $"get {ApiMe} failed");

			if(!Guid.TryParseExact(result.BodyAsString, "D", out var userId) || userId == default)
				throw new CheckerException(ExitCode.MUMBLE, $"invalid {ApiMe} response");

			await RndUtil.RndDelay(MaxDelay).ConfigureAwait(false);

			result = await client.DoRequestAsync(HttpMethod.Get, ApiList, null, null, NetworkOpTimeout, MaxHttpBodySize).ConfigureAwait(false);
			if(result.StatusCode != HttpStatusCode.OK)
				throw new CheckerException(result.StatusCode.ToExitCode(), $"get {ApiList} failed");

			var svgs = DoIt.TryOrDefault(() => JsonSerializer.Deserialize<List<Svg>>(result.BodyAsString));
			if(svgs == null)
				throw new CheckerException(ExitCode.MUMBLE, $"invalid {ApiList} response");

			await Console.Error.WriteLineAsync($"found '{svgs.Count}' svgs").ConfigureAwait(false);
		}

		public async Task<string> Put(string host, string id, string flag, int vuln)
		{
			var client = new AsyncHttpClient(GetBaseUri(host), true);

			var result = await client.DoRequestAsync(HttpMethod.Get, ApiMe, null, null, NetworkOpTimeout, MaxHttpBodySize).ConfigureAwait(false);
			if(result.StatusCode != HttpStatusCode.OK)
				throw new CheckerException(result.StatusCode.ToExitCode(), $"get {ApiMe} failed");

			if(!Guid.TryParseExact(result.BodyAsString, "D", out var userId) || userId == default)
				throw new CheckerException(ExitCode.MUMBLE, $"invalid {ApiMe} response");

			await RndUtil.RndDelay(MaxDelay).ConfigureAwait(false);

			var svg = RndSvg.Generate(flag);
			await Console.Error.WriteLineAsync(svg).ConfigureAwait(false);

			var data = $"data={WebUtility.UrlEncode(svg)}&isPrivate=true";
			result = await client.DoRequestAsync(HttpMethod.Post, ApiSvg, new Dictionary<string, string> {{"Content-Type", "application/x-www-form-urlencoded"}}, Encoding.UTF8.GetBytes(data), NetworkOpTimeout).ConfigureAwait(false);
			if(result.StatusCode != HttpStatusCode.OK)
				throw new CheckerException(result.StatusCode.ToExitCode(), $"post {ApiSvg} failed");

			if(!Guid.TryParseExact(result.BodyAsString, "D", out var fileId) || userId == default)
				throw new CheckerException(ExitCode.MUMBLE, $"invalid {ApiSvg} response");

			var cookie = client.Cookies.GetCookieHeader(GetBaseUri(host));
			await Console.Error.WriteLineAsync($"cookie '{cookie}'").ConfigureAwait(false);

			var bytes = DoIt.TryOrDefault(() => Encoding.UTF8.GetBytes(cookie));
			if(bytes == null || bytes.Length > 1024)
				throw new CheckerException(ExitCode.MUMBLE, "too large or invalid cookies");

			await RndUtil.RndDelay(MaxDelay).ConfigureAwait(false);

			client = new AsyncHttpClient(GetBaseUri(host));

			result = await client.DoRequestAsync(HttpMethod.Get, ApiList, null, null, NetworkOpTimeout, MaxHttpBodySize).ConfigureAwait(false);
			if(result.StatusCode != HttpStatusCode.OK)
				throw new CheckerException(result.StatusCode.ToExitCode(), $"get {ApiList} failed");

			var svgs = DoIt.TryOrDefault(() => JsonSerializer.Deserialize<List<Svg>>(result.BodyAsString));
			if(svgs == null)
				throw new CheckerException(ExitCode.MUMBLE, $"invalid {ApiList} response");

			if(!svgs.Any(svg => svg.UserId == userId && svg.FileId == fileId))
				throw new CheckerException(ExitCode.MUMBLE, $"posted svg not found in {ApiList} response");

			return $"{userId}:{fileId}:{Convert.ToBase64String(bytes)}";
		}

		public async Task Get(string host, string id, string flag, int vuln)
		{
			var parts = id.Split(':', 3);
			if(parts.Length != 3 || !Guid.TryParse(parts[0], out var userId) || !Guid.TryParse(parts[1], out var fileId))
				throw new Exception($"Invalid flag id '{id}'");

			var cookie = Encoding.UTF8.GetString(Convert.FromBase64String(parts[2]));

			var client = new AsyncHttpClient(GetBaseUri(host), true);

			await Console.Error.WriteLineAsync($"login by cookie '{cookie}'").ConfigureAwait(false);
			client.Cookies.SetCookies(GetBaseUri(host), cookie);

			var result = await client.DoRequestAsync(HttpMethod.Get, ApiMe, null, null, NetworkOpTimeout, MaxHttpBodySize).ConfigureAwait(false);
			if(result.StatusCode != HttpStatusCode.OK)
				throw new CheckerException(result.StatusCode.ToExitCode(), $"get {ApiMe} failed");

			if(!Guid.TryParseExact(result.BodyAsString, "D", out var me))
				throw new CheckerException(ExitCode.MUMBLE, $"invalid {ApiMe} response");

			if(me != userId)
				throw new CheckerException(ExitCode.MUMBLE, $"auth failed: {ApiMe} response changed");

			await RndUtil.RndDelay(MaxDelay).ConfigureAwait(false);

			var query = $"?userId={userId}&fileId={fileId}&isPrivate=true";

			result = await client.DoRequestAsync(HttpMethod.Get, ApiPdf + query, null, null, NetworkOpTimeout, MaxHttpBodySize).ConfigureAwait(false);
			if(result.StatusCode != HttpStatusCode.OK)
				throw new CheckerException(result.StatusCode.ToExitCode(), $"get {ApiPdf} failed");

			if(!(result.Body?.Length > PdfSign.Length) || Encoding.ASCII.GetString(result.Body.GetBuffer(), 0, PdfSign.Length) != PdfSign)
				throw new CheckerException(ExitCode.MUMBLE, $"invalid {ApiPdf} response");

			var parsed = DoIt.TryOrDefault(() => PdfUtils.PdfFirstPage2Text(result.Body, MaxPdfTextSize));
			if(parsed == null || !parsed.Contains(flag))
				throw new CheckerException(ExitCode.MUMBLE, $"invalid {ApiPdf} response");

			await RndUtil.RndDelay(MaxDelay).ConfigureAwait(false);

			result = await client.DoRequestAsync(HttpMethod.Get, ApiSvg + query, null, null, NetworkOpTimeout, MaxHttpBodySize).ConfigureAwait(false);
			if(result.StatusCode != HttpStatusCode.OK)
				throw new CheckerException(result.StatusCode.ToExitCode(), $"get {ApiSvg} failed");

			var svg = result.BodyAsString;
			if(svg == null || !svg.Contains(flag))
				throw new CheckerException(ExitCode.CORRUPT, "flag not found");
		}

		private const int Port = 5073;

		private const int MaxHttpBodySize = 512 * 1024;
		private const int NetworkOpTimeout = 10000;

		private const int MaxDelay = 1000;

		private static Uri GetBaseUri(string host) => new($"http://{host}:{Port}/");

		private const string ApiMe = "/api/me";
		private const string ApiList = "/api/list";
		private const string ApiSvg = "/api/svg";
		private const string ApiPdf = "/api/pdf";

		private static readonly string PdfSign = "%PDF";
		private const int MaxPdfTextSize = 65536;
	}
}
