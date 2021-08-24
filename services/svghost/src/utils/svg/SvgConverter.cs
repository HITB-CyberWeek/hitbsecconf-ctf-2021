using System;
using System.IO;
using System.Runtime.ExceptionServices;
using System.Runtime.InteropServices;
using System.Security;

namespace svghost.utils.svg
{
	public class SvgConversionException : Exception
	{
		public SvgConversionException(string message) : base(message) { }
	}

	public static class SvgConverter
	{
		static SvgConverter() { rsvg_set_default_dpi(72.0); }

		[SecurityCritical]
		[HandleProcessCorruptedStateExceptions]
		public static long WriteToPdf(string filepath, Stream stream)
		{
			var handle = rsvg_handle_new_from_file(filepath, out _);
			if(handle == IntPtr.Zero)
				throw new SvgConversionException("Failed to load svg");

			try
			{
				var dim = new RsvgDimensionData();
				rsvg_handle_get_dimensions(handle, ref dim);

				long total = 0;
				CairoStatus Write(IntPtr closure, byte[] data, uint length)
				{
					if(data == null || length > (uint)data.Length)
						return CairoStatus.CAIRO_STATUS_WRITE_ERROR;
					if(length == 0)
						return CairoStatus.CAIRO_STATUS_SUCCESS;
					try { stream.Write(data, 0, (int)length); }
					catch { return CairoStatus.CAIRO_STATUS_WRITE_ERROR; }
					total += length;

					return CairoStatus.CAIRO_STATUS_SUCCESS;
				}

				if(dim.width > MaxDimensionsSize || dim.height > MaxDimensionsSize)
					throw new SvgConversionException("Too large svg dimensions");

				var surface = cairo_pdf_surface_create_for_stream(Marshal.GetFunctionPointerForDelegate((CairoWriteFunc)Write), IntPtr.Zero, dim.width, dim.height);
				if(cairo_surface_status(surface) != CairoStatus.CAIRO_STATUS_SUCCESS)
					throw new SvgConversionException("Failed to create cairo surface");

				try
				{
					var cairo = cairo_create(surface);
					if(cairo_status(cairo) != CairoStatus.CAIRO_STATUS_SUCCESS)
						throw new SvgConversionException("Failed to create cairo rendering context");

					try
					{
						if(!rsvg_handle_render_cairo(handle, cairo))
							throw new SvgConversionException("Failed to render svg");
					}
					finally
					{
						cairo_destroy(cairo);
					}
				}
				finally
				{
					cairo_surface_destroy(surface);
				}

				return total;
			}
			finally
			{
				rsvg_handle_free(handle);
			}
		}

		private const string LibrsvgDllName = "librsvg-2";
		private const string LibcairoDllName = "libcairo";

		[DllImport(LibrsvgDllName, CallingConvention = CallingConvention.Cdecl)]
		private static extern void rsvg_set_default_dpi(double dpi);

		[DllImport(LibrsvgDllName, CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Ansi)]
		private static extern IntPtr rsvg_handle_new_from_file([MarshalAs(UnmanagedType.LPStr)] string file_name, out IntPtr error);

		[DllImport(LibrsvgDllName, CallingConvention = CallingConvention.Cdecl)]
		private static extern void rsvg_handle_get_dimensions(IntPtr handle, ref RsvgDimensionData dimension_data);

		[DllImport(LibrsvgDllName, CallingConvention = CallingConvention.Cdecl)]
		private static extern bool rsvg_handle_render_cairo(IntPtr handle, IntPtr cairo);

		[DllImport(LibrsvgDllName, CallingConvention = CallingConvention.Cdecl)]
		private static extern void rsvg_handle_free(IntPtr handle);

		[DllImport(LibcairoDllName, CallingConvention = CallingConvention.Cdecl)]
		private static extern IntPtr cairo_create(IntPtr target);

		[DllImport(LibcairoDllName, CallingConvention = CallingConvention.Cdecl)]
		private static extern CairoStatus cairo_status(IntPtr cairo);

		[DllImport(LibcairoDllName, CallingConvention = CallingConvention.Cdecl)]
		private static extern void cairo_destroy(IntPtr cairo);

		[UnmanagedFunctionPointer(CallingConvention.Cdecl)]
		private delegate CairoStatus CairoWriteFunc(IntPtr closure, [MarshalAs(UnmanagedType.LPArray, SizeParamIndex = 2)] byte[] data, uint length);

		[DllImport(LibcairoDllName, CallingConvention = CallingConvention.Cdecl)]
		private static extern IntPtr cairo_pdf_surface_create_for_stream(IntPtr write_func, IntPtr closure, double width, double height);

		[DllImport(LibcairoDllName, CallingConvention = CallingConvention.Cdecl)]
		private static extern CairoStatus cairo_surface_status(IntPtr surface);

		[DllImport(LibcairoDllName, CallingConvention = CallingConvention.Cdecl)]
		private static extern void cairo_surface_destroy(IntPtr cairo);

		[StructLayout(LayoutKind.Sequential, Pack = 1)]
		private struct RsvgDimensionData
		{
			public readonly int width;
			public readonly int height;
			public readonly double em;
			public readonly double ex;
		}

		private enum CairoStatus
		{
			CAIRO_STATUS_SUCCESS = 0,
			CAIRO_STATUS_NO_MEMORY,
			CAIRO_STATUS_INVALID_RESTORE,
			CAIRO_STATUS_INVALID_POP_GROUP,
			CAIRO_STATUS_NO_CURRENT_POINT,
			CAIRO_STATUS_INVALID_MATRIX,
			CAIRO_STATUS_INVALID_STATUS,
			CAIRO_STATUS_NULL_POINTER,
			CAIRO_STATUS_INVALID_STRING,
			CAIRO_STATUS_INVALID_PATH_DATA,
			CAIRO_STATUS_READ_ERROR,
			CAIRO_STATUS_WRITE_ERROR,
			CAIRO_STATUS_SURFACE_FINISHED,
			CAIRO_STATUS_SURFACE_TYPE_MISMATCH,
			CAIRO_STATUS_PATTERN_TYPE_MISMATCH,
			CAIRO_STATUS_INVALID_CONTENT,
			CAIRO_STATUS_INVALID_FORMAT,
			CAIRO_STATUS_INVALID_VISUAL,
			CAIRO_STATUS_FILE_NOT_FOUND,
			CAIRO_STATUS_INVALID_DASH,
			CAIRO_STATUS_INVALID_DSC_COMMENT,
			CAIRO_STATUS_INVALID_INDEX,
			CAIRO_STATUS_CLIP_NOT_REPRESENTABLE,
			CAIRO_STATUS_TEMP_FILE_ERROR,
			CAIRO_STATUS_INVALID_STRIDE,
			CAIRO_STATUS_FONT_TYPE_MISMATCH,
			CAIRO_STATUS_USER_FONT_IMMUTABLE,
			CAIRO_STATUS_USER_FONT_ERROR,
			CAIRO_STATUS_NEGATIVE_COUNT,
			CAIRO_STATUS_INVALID_CLUSTERS,
			CAIRO_STATUS_INVALID_SLANT,
			CAIRO_STATUS_INVALID_WEIGHT,
			CAIRO_STATUS_INVALID_SIZE,
			CAIRO_STATUS_USER_FONT_NOT_IMPLEMENTED,
			CAIRO_STATUS_DEVICE_TYPE_MISMATCH,
			CAIRO_STATUS_DEVICE_ERROR,
			CAIRO_STATUS_INVALID_MESH_CONSTRUCTION,
			CAIRO_STATUS_DEVICE_FINISHED,
			CAIRO_STATUS_JBIG2_GLOBAL_MISSING,
			CAIRO_STATUS_PNG_ERROR,
			CAIRO_STATUS_FREETYPE_ERROR,
			CAIRO_STATUS_WIN32_GDI_ERROR,
			CAIRO_STATUS_TAG_ERROR
		}

		private const double MaxDimensionsSize = 1000.0;
	}
}
