using System.Net;

namespace checker.svghost
{
	internal class RndSvg
	{
		public static string Generate(string flag)
		{
			//TODO
			return $"<svg><text x=\"10\" y=\"10\" font-size=\"8\">{WebUtility.HtmlEncode(flag)}</text></svg>";
		}
	}
}
