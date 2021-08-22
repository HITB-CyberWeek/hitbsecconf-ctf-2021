using System;
using System.Text.Json.Serialization;

namespace checker.svghost
{
	public class Svg
	{
		[JsonPropertyName("date")] public DateTime Date { get; set; }
		[JsonPropertyName("userId")] public Guid UserId { get; set; }
		[JsonPropertyName("fileId")] public Guid FileId { get; set; }
	}
}
