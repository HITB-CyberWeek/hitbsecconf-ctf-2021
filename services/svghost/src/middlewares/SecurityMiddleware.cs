using System;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;

namespace svghost.middlewares
{
	public class SecurityHeadersMiddleware
	{
		public SecurityHeadersMiddleware(RequestDelegate next) => this.next = next;

		public async Task Invoke(HttpContext context)
		{
			context.Response.OnStarting(() => SetHeaders(context));

			await next.Invoke(context).ConfigureAwait(false);
		}

		private static Task SetHeaders(HttpContext context)
		{
			if(context?.Response.ContentType == null)
				return Task.CompletedTask;

			if(!context.Response.ContentType.StartsWith("text/html", StringComparison.OrdinalIgnoreCase))
				context.Response.Headers["X-Content-Type-Options"] = "nosniff";
			else
			{
				context.Response.Headers["X-UA-Compatible"] = "IE=edge";
				context.Response.Headers["X-Frame-Options"] = "deny";
				context.Response.Headers["Referrer-Policy"] = "same-origin";
				context.Response.Headers["X-XSS-Protection"] = "1; mode=block";
				context.Response.Headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self' 'unsafe-inline';";
			}

			return Task.CompletedTask;
		}

		private readonly RequestDelegate next;
	}

	public static class SecurityMiddlewareExtensions
	{
		public static IApplicationBuilder UseSecurityHeaders(this IApplicationBuilder builder)
			=> builder.UseMiddleware<SecurityHeadersMiddleware>();
	}
}
