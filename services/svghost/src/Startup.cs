using System;
using System.Collections.Generic;
using System.IO;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.DataProtection;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.StaticFiles;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.FileProviders;
using svghost.middlewares;

namespace svghost
{
	public class Startup
	{
		public void ConfigureServices(IServiceCollection services)
		{
			services.AddDataProtection().PersistKeysToFileSystem(new DirectoryInfo("settings")).SetApplicationName(nameof(svghost));
			services
				.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
				.AddCookie(CookieAuthenticationDefaults.AuthenticationScheme, options =>
				{
					options.Cookie.SameSite = SameSiteMode.Strict;
					options.Cookie.Name = "usr";
				});
			services.AddMvc();
			services.AddControllers();
		}

		public void Configure(IApplicationBuilder app)
		{
			app
				.UseSecurityHeaders()
				.UseStatusCodePages("text/plain; charset=utf-8", "{0} 👻")
				.UseDefaultFiles(new DefaultFilesOptions { DefaultFileNames = new List<string> { "index.html" } })
				.UseStaticFiles(StaticFileOptions)
				.UseAuthentication()
				.UseUserId()
				.UseRouting()
				.UseEndpoints(endpoints => endpoints.MapControllers());
		}

		private static readonly StaticFileOptions StaticFileOptions = new()
		{
			ContentTypeProvider = new FileExtensionContentTypeProvider(new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
			{
				{".txt", "text/plain; charset=utf-8"},

				{".htm", "text/html; charset=utf-8"},
				{".html", "text/html; charset=utf-8"},

				{".json", "application/json; charset=utf-8"},

				{".css", "text/css; charset=utf-8"},
				{".js", "application/javascript; charset=utf-8"},

				{".svg", "image/svg+xml"},
				{".gif", "image/gif"},
				{".png", "image/png"},
				{".jpg", "image/jpeg"},
				{".jpeg", "image/jpeg"},
				{".webp", "image/webp"},

				{".eot", "application/vnd.ms-fontobject"},
				{".woff", "application/font-woff"},
				{".woff2", "application/font-woff2"},

				{".ico", "image/x-icon"}
			}),
			FileProvider = new PhysicalFileProvider(Path.Combine(Directory.GetCurrentDirectory(), "wwwroot")),
			ServeUnknownFileTypes = false,
			OnPrepareResponse = ctx => ctx.Context.Response.Headers["Cache-Control"] = "public, max-age=2419200"
		};
	}
}
