using System;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Xml;
using checker.rnd;

namespace checker.svghost
{
	internal static class RndSvg
	{
		public static string Generate(string flag)
		{
			var width = RndUtil.GetInt(200, 999);
			var height = RndUtil.GetInt(200, 999);

			var stream = new MemoryStream();
			using var writer = XmlWriter.Create(stream, new XmlWriterSettings
			{
				Indent = RndUtil.Bool(),
				OmitXmlDeclaration = RndUtil.Bool(),
				NewLineChars = RndUtil.Choice("\r\n", "\n"),
				IndentChars = RndUtil.Choice("\t", "  ", "    "),
				Encoding = new UTF8Encoding(false)
			});

			writer.WriteStartDocument(RndUtil.Bool());
			writer.WriteStartElement("svg", RndUtil.Choice("http://www.w3.org/2000/svg", null));
			if(RndUtil.Bool()) writer.WriteAttributeString("version", "1.1");
			writer.WriteAttributeString("width", width.ToString(NumberFormatInfo.InvariantInfo));
			writer.WriteAttributeString("height", height.ToString(NumberFormatInfo.InvariantInfo));
			if(RndUtil.Bool()) writer.WriteAttributeString("viewBox", $"0 0 {width} {height}");

			if(RndUtil.Bool()) writer.RndText(rnd.RndText.RandomText(64), width, height);

			RndUtil.Choice<Action<XmlWriter, int, int>>(
				RndSimple,
				RndComplex
			)(writer, width, height);

			writer.RndText(flag, width, height);

			if(RndUtil.Bool()) writer.RndText(rnd.RndText.RandomText(64), width, height);

			writer.WriteEndElement();
			writer.Flush();

			return Encoding.UTF8.GetString(stream.GetBuffer(), 0, (int)stream.Length);
		}

		private static void RndSimple(this XmlWriter writer, int width, int height)
		{
			foreach(var _ in Enumerable.Range(0, RndUtil.GetInt(1, 3)))
				writer.RndRect(width, height);
		}

		private static void RndComplex(this XmlWriter writer, int width, int height)
		{
			var centerx = width / 2;
			var centery = height / 2;
			var count = RndUtil.GetInt(8, 33);
			var radius = RndUtil.GetInt(20, Math.Min(width, height) / 3);
			var size = RndUtil.GetInt(20, Math.Min(width, height) / 3);

			var strokeWidth = RndUtil.GetInt(1, 6);

			var red = RndUtil.GetInt(0, 256);
			var green = RndUtil.GetInt(0, 256);
			var blue = RndUtil.GetInt(0, 256);

			byte RndColorPart(int part, int i) => unchecked((byte)(part + i * 256 / count));

			for(int i = 0; i < count; i++)
			{
				var cx = centerx + radius * Math.Cos(i * 2 * Math.PI / count);
				var cy = centery + radius * Math.Sin(i * 2 * Math.PI / count);
				writer.WriteStartElement("circle");
				writer.WriteAttributeString("cx", cx.ToString("0.##", NumberFormatInfo.InvariantInfo));
				writer.WriteAttributeString("cy", cy.ToString("0.##", NumberFormatInfo.InvariantInfo));
				writer.WriteAttributeString("r", size.ToString(NumberFormatInfo.InvariantInfo));
				writer.WriteAttributeString("fill", "none");
				writer.WriteAttributeString("stroke", $"#{RndColorPart(red, i):x2}{RndColorPart(green, i):x2}{RndColorPart(blue, i):x2}");
				writer.WriteAttributeString("stroke-width", strokeWidth.ToString(NumberFormatInfo.InvariantInfo));
				writer.WriteEndElement();
			}
		}

		private static void RndRect(this XmlWriter writer, int width, int height)
		{
			int min = 3;
			var x = RndUtil.GetInt(min, width - min);
			var y = RndUtil.GetInt(min, height - min);
			writer.WriteStartElement("rect");
			writer.WriteAttributeString("x", x.ToString(NumberFormatInfo.InvariantInfo));
			writer.WriteAttributeString("y", y.ToString(NumberFormatInfo.InvariantInfo));
			writer.WriteAttributeString("width", RndUtil.GetInt(1, width - x).ToString(NumberFormatInfo.InvariantInfo));
			writer.WriteAttributeString("height", RndUtil.GetInt(1, height - y).ToString(NumberFormatInfo.InvariantInfo));
			writer.WriteAttributeString("fill", RndColor());
			writer.WriteAttributeString("stroke", RndColor());
			if(RndUtil.Bool()) writer.WriteAttributeString("transform", $"rotate({RndUtil.GetInt(0, 361)} {x} {y})");
			writer.WriteEndElement();
		}

		private static void RndText(this XmlWriter writer, string text, int width, int height)
		{
			int x = 0, y = 0;
			var fontSize = RndUtil.GetInt(2, Math.Min(24, 2 * Math.Min(width, height) / text.Length) + 1);
			var position = RndUtil.Choice(TextAnchor.Start, TextAnchor.End, TextAnchor.Middle);
			var min = Math.Max(10, fontSize);
			switch(position)
			{
				case TextAnchor.Start:
					x = RndUtil.GetInt(min, width / 4);
					y = RndUtil.Choice(min, height - min);
					break;
				case TextAnchor.End:
					x = RndUtil.GetInt(width - width / 4, width - min);
					y = RndUtil.Choice(min, height - min);
					break;
				case TextAnchor.Middle:
					x = RndUtil.GetInt(width / 2 - width / 4, width / 2 + width / 4);
					y = RndUtil.GetInt(height / 2 - height / 4, height / 2 + height / 4);
					break;
			}
			writer.WriteStartElement("text");
			writer.WriteAttributeString("x", x.ToString(NumberFormatInfo.InvariantInfo));
			writer.WriteAttributeString("y", y.ToString(NumberFormatInfo.InvariantInfo));
			writer.WriteAttributeString("font-size", fontSize.ToString(NumberFormatInfo.InvariantInfo));
			if(RndUtil.Bool()) writer.WriteAttributeString("font-family", RndUtil.Choice("serif", "monospace", "cursive"));
			writer.WriteAttributeString("text-anchor", position.ToString("G").ToLowerInvariant());
			writer.WriteAttributeString("fill", RndColor());
			if(RndUtil.Bool()) writer.WriteAttributeString("transform", $"scale({RndUtil.GetDouble() / 2 + 0.5:0.##}) rotate({(position == TextAnchor.Middle ? RndUtil.GetInt(0, 361) : 0)} {x} {y})");
			writer.WriteString(text);
			writer.WriteEndElement();
		}

		private static string RndColor() =>
			RndUtil.Choice<Func<string>>(
				() => $"#{RndUtil.GetInt(0, 0xffffff + 1):x6}",
				() => $"#{RndUtil.GetInt(0, 0xfff + 1):x3}",
				() => $"#rgb({RndUtil.GetInt(0, 256)}, {RndUtil.GetInt(0, 256)}, {RndUtil.GetInt(0, 256)})",
				() => $"#rgba({RndUtil.GetInt(0, 256)}, {RndUtil.GetInt(0, 256)}, {RndUtil.GetInt(0, 256)}, {RndUtil.GetInt(0, 128) + 128})"
			).Invoke();

		private enum TextAnchor
		{
			Start,
			Middle,
			End
		}
	}
}
