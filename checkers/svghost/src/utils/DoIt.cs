using System;

namespace checker.utils
{
	internal static class DoIt
	{
		public static T TryOrDefault<T>(Func<T> func)
		{
			try { return func(); } catch { return default; }
		}
	}
}
