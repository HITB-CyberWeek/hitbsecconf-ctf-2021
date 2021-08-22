using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace checker.net
{
	internal class AsyncHttpClient
	{
		public AsyncHttpClient(Uri baseUri, bool cookies = false)
		{
			this.baseUri = baseUri;
			Cookies = cookies ? new CookieContainer(4, 4, 4096) : null;
		}

		public async Task<HttpResult> DoRequestAsync(HttpMethod method, string relative, Dictionary<string, string> headers = null, byte[] data = null, int timeout = 10000, int maxBodySize = 64 * 1024)
		{
			HttpResult result;
			var stopwatch = new Stopwatch();
			try
			{
				using var client = CreateHttpClient(TimeSpan.FromMilliseconds(timeout), maxBodySize);
				var message = new HttpRequestMessage(method, relative) {Version = HttpVersion, Method = method, Content = data == null ? null : new ByteArrayContent(data)};

				if(headers != null)
				{
					foreach(var header in headers)
					{
						if(!message.Headers.TryAddWithoutValidation(header.Key, header.Value))
							message.Content?.Headers.TryAddWithoutValidation(header.Key, header.Value);
					}
				}

				await Console.Error.WriteLineAsync($"{method.ToString().ToLowerInvariant()} {relative}, send {data?.Length ?? 0} bytes").ConfigureAwait(false);

				stopwatch.Start();

				using var source = new CancellationTokenSource(timeout);
				try
				{
					result = await DoRequestAsync(client, message, maxBodySize, source.Token).ConfigureAwait(false);
				}
				catch(HttpRequestException e) { result = HttpResult.Timeout; }
				catch(TaskCanceledException) { result = HttpResult.Timeout; }
			}
			catch(Exception e)
			{
				result = HttpResult.Unknown;
				result.Exception = e;
			}

			stopwatch.Stop();
			result.Elapsed = stopwatch.Elapsed;

			await Console.Error.WriteLineAsync($"http {(int)result.StatusCode} {result.StatusDescription ?? "Unknown"}, recv {result.Body?.Length ?? 0} bytes, {stopwatch.ElapsedMilliseconds} ms").ConfigureAwait(false);

			return result;
		}

		private async Task<HttpResult> DoRequestAsync(HttpClient client, HttpRequestMessage request, int maxBodySize, CancellationToken token)
		{
			using var response = await client.SendAsync(request, HttpCompletionOption.ResponseContentRead, token).ConfigureAwait(false);
			if(response == null)
				return HttpResult.Unknown;

			var result = new HttpResult {StatusCode = response.StatusCode, StatusDescription = response.ReasonPhrase, Headers = response.Headers};
			await using var stream = await response.Content.ReadAsStreamAsync().ConfigureAwait(false);

			var ms = new MemoryStream(new byte[maxBodySize], 0, maxBodySize, true, true);
			ms.SetLength(0);

			await stream.CopyToAsync(ms, token).ConfigureAwait(false);

			ms.Seek(0, SeekOrigin.Begin);
			result.Body = ms;

			await stream.CopyToAsync(Stream.Null, token);

			return result;
		}

		private HttpClient CreateHttpClient(TimeSpan timeout, int maxBodySize)
		{
			var handler = new HttpClientHandler
			{
				ServerCertificateCustomValidationCallback = (_, __, ___, ____) => true,
				Proxy = null,
				UseProxy = false,
				UseDefaultCredentials = false,
				PreAuthenticate = false,
				MaxConnectionsPerServer = 1024,
				MaxResponseHeadersLength = 4096,
				UseCookies = Cookies != null
			};

			if(Cookies != null)
				handler.CookieContainer = Cookies;

			return new HttpClient(handler)
			{
				BaseAddress = baseUri,
				MaxResponseContentBufferSize = maxBodySize,
				Timeout = timeout
			};
		}

		public readonly CookieContainer Cookies;

		private static readonly Version HttpVersion = new Version(1, 1);
		private readonly Uri baseUri;
	}

	internal struct HttpResult
	{
		public HttpStatusCode StatusCode;
		public string StatusDescription;
		public HttpResponseHeaders Headers;

		public MemoryStream Body;
		public string BodyAsString => Body == null ? null : Encoding.UTF8.GetString(Body.GetBuffer(), 0, (int)Body.Length);
		public TimeSpan Elapsed;

		public Exception Exception;

		public static HttpResult Timeout => new HttpResult {StatusCode = (HttpStatusCode)499};
		public static HttpResult Unknown => new HttpResult();
	}
}
