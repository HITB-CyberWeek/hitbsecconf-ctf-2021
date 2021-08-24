using System.Collections.Generic;
using System.Runtime.CompilerServices;

namespace checker.utils
{
	internal static class CollectionUtils
	{
		[MethodImpl(MethodImplOptions.AggressiveInlining)]
		public static TValue GetOrDefault<TKey, TValue>(this Dictionary<TKey, TValue> dict, TKey key)
			=> dict.TryGetValue(key, out var value) ? value : default;
	}
}
