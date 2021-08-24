using System;

namespace checker
{
	internal class CheckerException : Exception
	{
		public CheckerException(ExitCode exitCode, string stdOut = null)
		{
			ExitCode = exitCode;
			StdOut = stdOut;
		}

		public readonly ExitCode ExitCode;
		public readonly string StdOut;
	}
}
