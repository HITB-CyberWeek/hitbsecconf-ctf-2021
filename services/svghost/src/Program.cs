using System;
using System.IO;
using System.Net;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Server.Kestrel.Core;
using Microsoft.Extensions.Logging;

namespace svghost
{
	static class Program
	{
		static void Main()
		{
			new WebHostBuilder()
				.ConfigureLogging(builder => builder.AddConsole())
				.UseKestrel(options =>
				{
					options.Listen(IPAddress.Loopback, 5073);
					options.AddServerHeader = false;
					options.Limits.KeepAliveTimeout = TimeSpan.FromSeconds(30.0);
					options.Limits.MaxRequestBodySize = 65536L;
					options.Limits.MaxRequestLineSize = 4096;
					options.Limits.MaxRequestHeaderCount = 64;
					options.Limits.MaxRequestHeadersTotalSize = 8192;
					options.Limits.RequestHeadersTimeout = TimeSpan.FromSeconds(3.0);
					options.Limits.MinRequestBodyDataRate = new MinDataRate(32768.0, TimeSpan.FromSeconds(3.0));
					options.Limits.MinResponseDataRate = new MinDataRate(32768.0, TimeSpan.FromSeconds(3.0));
				}).UseContentRoot(Directory.GetCurrentDirectory()).UseStartup<Startup>().Build().Run();
		}
	}
}
