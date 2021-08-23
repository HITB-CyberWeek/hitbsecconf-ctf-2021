using System;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;

namespace checker.rnd
{
	internal static class RndUtil
	{
		[MethodImpl(MethodImplOptions.AggressiveInlining)]
		public static T Choice<T>(params T[] array) => array[ThreadStaticRnd.Next(array.Length)];

		[MethodImpl(MethodImplOptions.AggressiveInlining)]
		public static char Choice(string str) => str[ThreadStaticRnd.Next(str.Length)];

		[MethodImpl(MethodImplOptions.AggressiveInlining)]
		public static int GetInt(int inclusiveMinValue, int exclusiveMaxValue) => ThreadStaticRnd.Next(inclusiveMinValue, exclusiveMaxValue);

		public static bool Bool() => ThreadStaticRnd.Next(2) == 0;

		public static Random ThreadStaticRnd => rnd ??= new Random(Guid.NewGuid().GetHashCode());

		public static Task RndDelay(int max) => Task.Delay(ThreadStaticRnd.Next(max));

		[ThreadStatic] private static Random rnd;
	}
}
