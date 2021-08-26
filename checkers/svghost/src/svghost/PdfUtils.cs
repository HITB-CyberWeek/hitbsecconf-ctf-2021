using System;
using System.IO;
using System.Text;
using iTextSharp.text;
using iTextSharp.text.pdf;

namespace checker.svghost
{
	internal static class PdfUtils
	{
		public static string OnePagePdf2Text(Stream stream, int maxSize, out Rectangle size)
		{
			var reader = new PdfReader(stream);
			try
			{
				if(reader.NumberOfPages != 1)
					throw new Exception("expected PDF with only one page");
				size = reader.GetPageSize(1);
				var builder = new StringBuilder(1024, maxSize);
				var tokenizer = new PRTokeniser(reader.GetPageContent(1));
				try
				{
					var parser = new PdfContentParser(tokenizer);
					while(parser.Tokeniser.NextToken())
					{
						if(parser.Tokeniser.TokenType == PRTokeniser.TK_STRING)
							builder.Append(parser.Tokeniser.StringValue);
					}
					return builder.ToString();
				}
				finally
				{
					tokenizer.Close();
				}
			}
			finally
			{
				reader.Close();
			}
		}
	}
}
