using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Xml;

namespace svghost.utils.svg
{
	public static class SvgSanitizer
	{
		public static string Sanitize(string data)
		{
			var doc = new XmlDocument {XmlResolver = null!};
			doc.Load(XmlReader.Create(new StringReader(data), XmlSettings));
			SanitizeNodes(doc, 0);
			return doc.InnerXml;
		}

		private static void SanitizeNodes(XmlNode current, int level)
		{
			foreach(XmlNode node in current.ChildNodes)
			{
				if(node.NodeType == XmlNodeType.XmlDeclaration)
					continue;

				if(level >= MaxNodeLevel || UnsafeNodeTypes.Contains(node.NodeType) || !AllowedTags.Contains(node.Name))
				{
					current.RemoveChild(node);
					continue;
				}

				SanitizeNodes(node, level + 1);

				if(node.Attributes == null)
					continue;

				foreach(var attr in node.Attributes.Cast<XmlAttribute>().ToList())
				{
					if(!AllowedAttributes.Contains(attr.Name) || ColorAttributes.Contains(attr.Name) && !ColorRegex.IsMatch(attr.Value))
						node.Attributes.Remove(attr);
				}
			}
		}

		private static readonly HashSet<XmlNodeType> UnsafeNodeTypes = new()
		{
			XmlNodeType.DocumentType,
			XmlNodeType.Entity,
			XmlNodeType.EntityReference,
			XmlNodeType.ProcessingInstruction
		};

		private static readonly HashSet<string> AllowedTags = new(StringComparer.OrdinalIgnoreCase)
		{
			"svg", "xml", "g",
			"path", "line", "polyline",
			"rect", "circle", "ellipse", "polygon",
			"text", "tspan", "#text"
		};

		private static readonly HashSet<string> AllowedAttributes = new(StringComparer.OrdinalIgnoreCase)
		{
			"viewBox", "xmlns", "xmlns:svg", "version", "standalone", "encoding",
			"r", "r2", "x", "y", "dx", "dy", "x1", "y1", "x2", "y2", "cx", "cy", "rx", "ry", "width", "height",
			"d", "point", "points",
			"sides", "shape", "orient",
			"fill", "stroke",
			"stroke-width", "stroke-dasharray", "stroke-linecap", "stroke-linejoin",
			"transform", "rotate",
			"font-size", "text-anchor", "textLength", "lengthAdjust"
		};

		private static readonly HashSet<string> ColorAttributes = new(StringComparer.OrdinalIgnoreCase)
		{
			"fill", "stroke"
		};

		//NOTE: url(resource) is prohibited here
		private static readonly Regex ColorRegex = new(@"^(?:[a-z]+|#[\da-f]{3}(?:[\da-f]{3})?|(?:rgba?|hsla?)\([^\)]*\))$", RegexOptions.Compiled | RegexOptions.CultureInvariant | RegexOptions.IgnoreCase);
		private static readonly XmlReaderSettings XmlSettings = new()
		{
			XmlResolver = null,
			DtdProcessing = DtdProcessing.Prohibit,
			MaxCharactersFromEntities = 1024,
			MaxCharactersInDocument = 512 * 1024,
			IgnoreProcessingInstructions = true
		};

		private const int MaxNodeLevel = 16;
	}
}
