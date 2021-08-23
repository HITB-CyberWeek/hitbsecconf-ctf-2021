using System;
using System.Globalization;
using System.IO;
using System.Text;
using System.Xml;
using checker.rnd;

namespace checker.svghost
{
	internal class RndSvg
	{
		public static string Generate(string text)
		{
			var width = RndUtil.GetInt(200, 999);
			var height = RndUtil.GetInt(200, 999);
			var fontSize = RndUtil.GetInt(1, Math.Min(20, width / text.Length) + 1);

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
			{
				var centerx = width / 2;
				var centery = height / 2;
				var count = RndUtil.GetInt(8, 33);
				var radius = RndUtil.GetInt(20, Math.Min(width, height) / 3);
				var size = RndUtil.GetInt(20, Math.Min(width, height) / 3);

				var red = RndUtil.GetInt(0, 256);
				var green = RndUtil.GetInt(0, 256);
				var blue = RndUtil.GetInt(0, 256);

				var strokeWidth = RndUtil.GetInt(1, 16);

				for(double i = 0; i < count; i++)
				{
					var cx = centerx + radius * Math.Cos(i * 2 * Math.PI / count);
					var cy = centery + radius * Math.Sin(i * 2 * Math.PI / count);
					writer.WriteStartElement("circle");
					writer.WriteAttributeString("cx", cx.ToString("0.##", NumberFormatInfo.InvariantInfo));
					writer.WriteAttributeString("cy", cy.ToString("0.##", NumberFormatInfo.InvariantInfo));
					writer.WriteAttributeString("r", size.ToString(NumberFormatInfo.InvariantInfo));
					writer.WriteAttributeString("fill", "none");
					writer.WriteAttributeString("stroke", $"#{unchecked((byte)(red + i * 256 / count)):x2}{unchecked((byte)(green + i * 256 / count)):x2}{unchecked((byte)(blue + i * 256 / count)):x2}");
					writer.WriteAttributeString("stroke-width", strokeWidth.ToString(NumberFormatInfo.InvariantInfo));
					writer.WriteEndElement();
				}

				writer.WriteStartElement("text");
				writer.WriteAttributeString("x", 10.ToString(NumberFormatInfo.InvariantInfo));
				writer.WriteAttributeString("y", 10.ToString(NumberFormatInfo.InvariantInfo));
				writer.WriteAttributeString("font-size", fontSize.ToString(NumberFormatInfo.InvariantInfo));
				writer.WriteString(text);
				writer.WriteEndElement();
			}
			writer.WriteEndElement();
			writer.Flush();

			return Encoding.UTF8.GetString(stream.GetBuffer(), 0, (int)stream.Length);
		}
	}
}
