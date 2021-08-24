using System;
using System.Collections.Generic;
using System.Security.Claims;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;

namespace svghost.middlewares
{
	public class AuthMiddleware
	{
		public AuthMiddleware(RequestDelegate next) => this.next = next;

		public async Task Invoke(HttpContext context)
		{
			await SignInAsync(context);
			await next.Invoke(context);
		}

		private static async Task SignInAsync(HttpContext context)
		{
			if(context.User.FindUserId() != default)
				return;

			var name = Guid.NewGuid().ToString("N");
			var principal = new ClaimsPrincipal(new ClaimsIdentity(new List<Claim> { new(ClaimTypes.Name, name) }, CookieAuthenticationDefaults.AuthenticationScheme));
			context.User = principal;
			await context.SignInAsync(CookieAuthenticationDefaults.AuthenticationScheme, principal);
		}

		private readonly RequestDelegate next;
	}

	public static class AuthMiddlewareExtensions
	{
		public static IApplicationBuilder UseUserId(this IApplicationBuilder builder)
			=> builder.UseMiddleware<AuthMiddleware>();
	}

	public static class AuthController
	{
		public static Guid FindUserId(this ClaimsPrincipal principal)
			=> Guid.TryParseExact(principal?.Identity?.Name, "N", out var id) ? id : default;
	}
}
