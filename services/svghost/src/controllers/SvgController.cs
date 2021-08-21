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
		public async Task<IActionResult> Me()
		{
			var userId = User.FindUserId();
			return userId == default ? StatusCode(401, "👻 not authenticated") : Ok(userId.ToString());
		}

		[HttpGet("/api/svg")]
		public async Task<IActionResult> GetRaw(Guid fileId)
		{
			var userId = User.FindUserId();
			if(userId == default)
				return StatusCode(401, "👻 not authenticated");

			var text = await SvgStore.FindDataAsync(userId, fileId, sanitized: false);
			if(text == null)
				return StatusCode(404, "👻 not found");

			Response.ContentType = "text/svg+xml";
			return Content(text);
		}

		[HttpGet("/api/pdf")]
		public async Task<IActionResult> GetPdf(Guid userId, Guid fileId)
		{
			var file = SvgStore.FindFilePath(userId == default ? User.FindUserId() : userId, fileId, sanitized: true);
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
				return StatusCode(400, "👻 empty");

			string sanitized;
			try { sanitized = SvgSanitizer.Sanitize(data); }
			catch { return StatusCode(400, "👻 invalid"); }

			var fileId = Guid.NewGuid();
			await SvgStore.SaveAsync(userId, fileId, data, sanitized);

			return Ok(fileId.ToString());
		}

		[HttpGet("/api/list")]
		public async Task<IActionResult> List(int skip, int take = 1000)
			=> Ok(SvgStore.List().Skip(skip).Take(Math.Min(1000, take)));

		private const int MaxPdfFileSize = 512 * 1024;
		private static readonly EmptyResult EmptyResult = new();
	}
}
