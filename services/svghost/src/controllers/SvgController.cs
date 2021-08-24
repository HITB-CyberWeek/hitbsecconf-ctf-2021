using System;
using System.Buffers;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using svghost.middlewares;
using svghost.utils.svg;

namespace svghost.controllers
{
	[ApiController]
	public class SvgController : ControllerBase
	{
		[HttpGet("/api/me")]
		public IActionResult Me()
		{
			var userId = User.FindUserId();
			return userId == default ? StatusCode(401, "👻 not authenticated") : Ok(userId.ToString());
		}

		[HttpGet("/api/svg")]
		public async Task<IActionResult> GetRaw(Guid userId, Guid fileId, bool isPrivate)
		{
			if(User.FindUserId() != userId)
				return StatusCode(403, "👻 not authorized");

			var text = await SvgStore.FindDataAsync(userId, fileId, isPrivate, sanitized: false);
			if(text == null)
				return StatusCode(404, "👻 not found");

			Response.ContentType = "text/plain";
			return Content(text);
		}

		[HttpGet("/api/pdf")]
		public async Task<IActionResult> GetPdf(Guid userId, Guid fileId, bool isPrivate)
		{
			if(isPrivate && userId != User.FindUserId())
				return StatusCode(403, "👻 not authorized");

			var file = SvgStore.FindFilePath(userId == default ? User.FindUserId() : userId, fileId, isPrivate, sanitized: true);
			if(file == null)
				return StatusCode(404, "👻 not found");

			var buffer = ArrayPool<byte>.Shared.Rent(MaxPdfFileSize);
			try
			{
				await using var stream = new MemoryStream(buffer, true); //NOTE: sync IO is prohibited so we use MemoryStream buffer here
				var length = SvgConverter.WriteToPdf(file, stream);
				Response.ContentType = "application/pdf";
				await Response.Body.WriteAsync(buffer, 0, (int)length);
				return EmptyResult;
			}
			catch(SvgConversionException e)
			{
				return StatusCode(500, e.Message);
			}
			finally
			{
				ArrayPool<byte>.Shared.Return(buffer);
			}
		}

		[HttpPost("/api/svg")]
		public async Task<IActionResult> Post()
		{
			var userId = User.FindUserId();
			if(userId == default)
				return StatusCode(401, "👻 not authenticated");

			var data = Request.Form["data"].FirstOrDefault();
			if(string.IsNullOrEmpty(data))
				return StatusCode(400, "👻 empty svg");

			bool.TryParse(Request.Form["isPrivate"].FirstOrDefault(), out var isPrivate);

			string sanitized;
			try { sanitized = SvgSanitizer.Sanitize(data); }
			catch { return StatusCode(400, "👻 invalid svg"); }

			var fileId = Guid.NewGuid();
			await SvgStore.SaveAsync(userId, fileId, isPrivate, data, sanitized);

			return Ok(fileId.ToString());
		}

		[HttpGet("/api/list")]
		public IActionResult List(int skip, int take = 1000)
			=> Ok(SvgStore.List().Skip(skip).Take(Math.Min(1000, take)));

		private const int MaxPdfFileSize = 512 * 1024;
		private static readonly EmptyResult EmptyResult = new();
	}
}
