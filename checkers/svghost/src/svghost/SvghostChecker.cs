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
				throw new CheckerException(result.StatusCode.ToExitCode(), $"get / failed: {result.StatusCode.ToReadableCode()}");

			await RndUtil.RndDelay(MaxDelay).ConfigureAwait(false);

			result = await client.DoRequestAsync(HttpMethod.Get, ApiMe, null, null, NetworkOpTimeout, MaxHttpBodySize).ConfigureAwait(false);
			if(result.StatusCode != HttpStatusCode.OK)
				throw new CheckerException(result.StatusCode.ToExitCode(), $"get {ApiMe} failed: {result.StatusCode.ToReadableCode()}");

			if(!Guid.TryParseExact(result.BodyAsString, "D", out var userId) || userId == default)
				throw new CheckerException(ExitCode.MUMBLE, $"invalid {ApiMe} response: uuid expected");

			await Console.Error.WriteLineAsync($"userId '{userId}'").ConfigureAwait(false);
		}

		public async Task<string> Put(string host, string id, string flag, int vuln)
		{
			var client = new AsyncHttpClient(GetBaseUri(host), true);

			var result = await client.DoRequestAsync(HttpMethod.Get, ApiMe, null, null, NetworkOpTimeout, MaxHttpBodySize).ConfigureAwait(false);
			if(result.StatusCode != HttpStatusCode.OK)
				throw new CheckerException(result.StatusCode.ToExitCode(), $"get {ApiMe} failed: {result.StatusCode.ToReadableCode()}");

			if(!Guid.TryParseExact(result.BodyAsString, "D", out var userId) || userId == default)
				throw new CheckerException(ExitCode.MUMBLE, $"invalid {ApiMe} response: uuid expected");

			await Console.Error.WriteLineAsync($"userId '{userId}'").ConfigureAwait(false);

			var files = new List<(string unique, Guid fileId)>();
			async Task PutPublicFileIfRnd(AsyncHttpClient client)
			{
				if(RndUtil.GetInt(0, 9) != 0)
					return;

				var unique = Guid.NewGuid().ToString();
				var publicFileId = await PutPublicPdf(client, unique).ConfigureAwait(false);

				files.Add((unique, fileId: publicFileId));
			}

			await RndUtil.RndDelay(MaxDelay).ConfigureAwait(false);
			await PutPublicFileIfRnd(client).ConfigureAwait(false);
			await RndUtil.RndDelay(MaxDelay).ConfigureAwait(false);

			var svg = RndSvg.Generate(flag);
			await Console.Error.WriteLineAsync($"private svg '{SvgToLog(svg)}'").ConfigureAwait(false);

			var data = $"data={WebUtility.UrlEncode(svg)}&isPrivate=true";
			result = await client.DoRequestAsync(HttpMethod.Post, ApiSvg, new Dictionary<string, string> {{"Content-Type", "application/x-www-form-urlencoded"}}, Encoding.UTF8.GetBytes(data), NetworkOpTimeout).ConfigureAwait(false);
			if(result.StatusCode != HttpStatusCode.OK)
				throw new CheckerException(result.StatusCode.ToExitCode(), $"post {ApiSvg} failed: {result.StatusCode.ToReadableCode()}");

			if(!Guid.TryParseExact(result.BodyAsString, "D", out var fileId) || fileId == default)
				throw new CheckerException(ExitCode.MUMBLE, $"invalid {ApiSvg} response: uuid expected");

			var cookie = client.Cookies?.GetCookieHeader(GetBaseUri(host));
			await Console.Error.WriteLineAsync($"cookie '{(cookie?.Length > MaxCookieSize ? cookie.Substring(0, MaxCookieSize) + "..." : cookie)}' with length '{cookie?.Length ?? 0}'").ConfigureAwait(false);

			if(cookie == null || cookie.Length > MaxCookieSize)
				throw new CheckerException(ExitCode.MUMBLE, "too large or invalid cookies");

			var bytes = DoIt.TryOrDefault(() => Encoding.UTF8.GetBytes(cookie));
			if(bytes == null || bytes.Length > MaxCookieSize)
				throw new CheckerException(ExitCode.MUMBLE, "too large or invalid cookies");

			await RndUtil.RndDelay(MaxDelay).ConfigureAwait(false);
			await PutPublicFileIfRnd(client).ConfigureAwait(false);
			await RndUtil.RndDelay(MaxDelayBeforeList).ConfigureAwait(false);

			client = new AsyncHttpClient(GetBaseUri(host)); //NOTE: Discard cookies and check listing

			int skip = 0;
			Svg found = null;
			for(int i = 0; i < 5; i++)
			{
				var query = $"?skip={skip}&take=1000";
				result = await client.DoRequestAsync(HttpMethod.Get, ApiList + query, null, null, NetworkOpTimeout, MaxHttpBodySize).ConfigureAwait(false);
				if(result.StatusCode != HttpStatusCode.OK)
					throw new CheckerException(result.StatusCode.ToExitCode(), $"get {ApiList} failed: {result.StatusCode.ToReadableCode()}");

				var svgs = DoIt.TryOrDefault(() => JsonSerializer.Deserialize<List<Svg>>(result.BodyAsString));
				if(svgs == null)
					throw new CheckerException(ExitCode.MUMBLE, $"invalid {ApiList} response: svg collection expected");

				await Console.Error.WriteLineAsync($"found '{svgs.Count}' svgs").ConfigureAwait(false);

				found = svgs.FirstOrDefault(svg => svg.UserId == userId && svg.FileId == fileId);
				if(found != null || svgs.Count == 0)
					break;

				skip = svgs.Count;
			}

			if(found == null)
				throw new CheckerException(ExitCode.MUMBLE, $"posted svg not found in {ApiList} response");

			foreach(var publicFileId in files)
			{
				await RndUtil.RndDelay(MaxDelay).ConfigureAwait(false);
				await CheckPublicPdfContainsText(client, userId, publicFileId.fileId, publicFileId.unique).ConfigureAwait(false);
			}

			return $"{userId}:{fileId}:{Convert.ToBase64String(bytes)}";
		}

		public async Task Get(string host, string id, string flag, int vuln)
		{
			var parts = id.Split(':', 3);
			if(parts.Length != 3 || !Guid.TryParse(parts[0], out var userId) || !Guid.TryParse(parts[1], out var fileId))
				throw new Exception($"Invalid flag id '{id}'");

			var cookie = Encoding.UTF8.GetString(Convert.FromBase64String(parts[2]));

			var client = new AsyncHttpClient(GetBaseUri(host), true);

			await Console.Error.WriteLineAsync($"saved userId '{userId}', saved fileId '{fileId}', use cookie '{cookie}'").ConfigureAwait(false);
			client.Cookies.SetCookies(GetBaseUri(host), cookie);

			var result = await client.DoRequestAsync(HttpMethod.Get, ApiMe, null, null, NetworkOpTimeout, MaxHttpBodySize).ConfigureAwait(false);
			if(result.StatusCode != HttpStatusCode.OK)
				throw new CheckerException(result.StatusCode.ToExitCode(), $"get {ApiMe} failed: {result.StatusCode.ToReadableCode()}");

			if(!Guid.TryParseExact(result.BodyAsString, "D", out var me))
				throw new CheckerException(ExitCode.MUMBLE, $"invalid {ApiMe} response: uuid expected");

			await Console.Error.WriteLineAsync($"userId '{me}'").ConfigureAwait(false);

			if(me != userId)
				throw new CheckerException(ExitCode.MUMBLE, $"auth failed: {ApiMe} uuid mismatch");

			await RndUtil.RndDelay(MaxDelay).ConfigureAwait(false);

			var query = $"?userId={userId}&fileId={fileId}&isPrivate=true";

			result = await client.DoRequestAsync(HttpMethod.Get, ApiPdf + query, null, null, NetworkOpTimeout, MaxHttpBodySize).ConfigureAwait(false);
			if(result.StatusCode == HttpStatusCode.NotFound)
				throw new CheckerException(ExitCode.CORRUPT, $"get {ApiPdf} failed: {result.StatusCode.ToReadableCode()}");
			if(result.StatusCode != HttpStatusCode.OK)
				throw new CheckerException(result.StatusCode.ToExitCode(), $"get {ApiPdf} failed: {result.StatusCode.ToReadableCode()}");

			if(!(result.Body?.Length > PdfSign.Length) || Encoding.ASCII.GetString(result.Body.GetBuffer(), 0, PdfSign.Length) != PdfSign)
				throw new CheckerException(ExitCode.MUMBLE, $"invalid {ApiPdf} response: pdf expected");

			var parsed = DoIt.TryOrDefault(() => PdfUtils.PdfFirstPage2Text(result.Body, MaxPdfTextSize));
			if(parsed == null || !parsed.Contains(flag))
				throw new CheckerException(ExitCode.CORRUPT, $"invalid {ApiPdf} response: flag not found");

			await RndUtil.RndDelay(MaxDelay).ConfigureAwait(false);

			result = await client.DoRequestAsync(HttpMethod.Get, ApiSvg + query, null, null, NetworkOpTimeout, MaxHttpBodySize).ConfigureAwait(false);
			if(result.StatusCode == HttpStatusCode.NotFound)
				throw new CheckerException(ExitCode.CORRUPT, $"get {ApiSvg} failed: {result.StatusCode.ToReadableCode()}");
			if(result.StatusCode != HttpStatusCode.OK)
				throw new CheckerException(result.StatusCode.ToExitCode(), $"get {ApiSvg} failed: {result.StatusCode.ToReadableCode()}");

			var svg = result.BodyAsString;
			if(svg == null || !svg.Contains(flag))
				throw new CheckerException(ExitCode.CORRUPT, $"invalid {ApiSvg} response: flag not found");
		}

		private static async Task<Guid> PutPublicPdf(AsyncHttpClient client, string text)
		{
			var svg = RndSvg.Generate(text);
			await Console.Error.WriteLineAsync($"public svg '{SvgToLog(svg)}'").ConfigureAwait(false);

			var data = $"data={WebUtility.UrlEncode(svg)}&isPrivate=false";
			var result = await client.DoRequestAsync(HttpMethod.Post, ApiSvg, new Dictionary<string, string> {{"Content-Type", "application/x-www-form-urlencoded"}}, Encoding.UTF8.GetBytes(data), NetworkOpTimeout).ConfigureAwait(false);
			if(result.StatusCode != HttpStatusCode.OK)
				throw new CheckerException(result.StatusCode.ToExitCode(), $"post {ApiSvg} failed: {result.StatusCode.ToReadableCode()}");

			if(!Guid.TryParseExact(result.BodyAsString, "D", out var fileId) || fileId == default)
				throw new CheckerException(ExitCode.MUMBLE, $"invalid {ApiSvg} response: uuid expected");

			return fileId;
		}

		private static async Task CheckPublicPdfContainsText(AsyncHttpClient client, Guid userId, Guid fileId, string text)
		{
			var query = $"?userId={userId}&fileId={fileId}&isPrivate=false";
			var result = await client.DoRequestAsync(HttpMethod.Get, ApiPdf + query, null, null, NetworkOpTimeout, MaxHttpBodySize).ConfigureAwait(false);
			if(result.StatusCode != HttpStatusCode.OK)
				throw new CheckerException(result.StatusCode.ToExitCode(), $"get {ApiPdf} failed: {result.StatusCode.ToReadableCode()}");

			if(!(result.Body?.Length > PdfSign.Length) || Encoding.ASCII.GetString(result.Body.GetBuffer(), 0, PdfSign.Length) != PdfSign)
				throw new CheckerException(ExitCode.MUMBLE, $"invalid {ApiPdf} response: pdf expected");

			var parsed = DoIt.TryOrDefault(() => PdfUtils.PdfFirstPage2Text(result.Body, MaxPdfTextSize));
			if(parsed == null || !parsed.Contains(text))
				throw new CheckerException(ExitCode.MUMBLE, $"invalid {ApiPdf} response: invalid pdf");
		}

		private static string SvgToLog(string svg)
			=> svg.Length > 256 ? svg.Substring(0, 256).Replace('\r', ' ').Replace('\n', ' ') + "..." : svg.Replace('\r', ' ').Replace('\n', ' ');

		private const int Port = 5073;

		private const int MaxHttpBodySize = 512 * 1024;
		private const int MaxCookieSize = 1024;

		private const int MaxDelay = 1000;
		private const int MaxDelayBeforeList = 8000;
		private const int NetworkOpTimeout = 8000;

		private static Uri GetBaseUri(string host) => new($"http://{host}:{Port}/");

		private const string ApiMe = "/api/me";
		private const string ApiList = "/api/list";
		private const string ApiSvg = "/api/svg";
		private const string ApiPdf = "/api/pdf";

		private static readonly string PdfSign = "%PDF";
		private const int MaxPdfTextSize = 65536;
	}
}
