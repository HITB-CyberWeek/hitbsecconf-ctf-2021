using System.Net;

namespace checker.svghost
{
	internal class RndSvg
	{
		public static string Generate(string text, string flag)
		{
			//TODO
			return $"<svg><desc>{WebUtility.HtmlEncode(flag)}</desc><text x=\"10\" y=\"10\">{WebUtility.HtmlEncode(text)}</text></svg>";
		}
	}
}
