using System;
using System.Linq;
using System.Threading.Tasks;
using checker.svghost;
using checker.rnd;

namespace checker
{
	class Program
	{
		private static async Task<int> Main(string[] args)
		{
			try
			{
				var arguments = ParseArgs(args);
				var checker = new SvghostChecker();

				await Do(checker, arguments).ConfigureAwait(false);

				return (int)ExitCode.OK;
			}
			catch(Exception e)
			{
				var error = e as CheckerException ?? (e as AggregateException)?.Flatten().InnerExceptions?.OfType<CheckerException>().FirstOrDefault();
				if(error != null)
				{
					if(error.StdOut != null)
						Console.Out.WriteLine(error.StdOut);

					return (int)error.ExitCode;
				}

				Console.Error.WriteLine(e);
				return (int)ExitCode.CHECKER_ERROR;
			}
		}

		private static async Task Do(IChecker checker, CheckerArgs args)
		{
			switch(args.Command)
			{
				case Command.Debug:
					await Debug(checker, args.Host).ConfigureAwait(false);
					break;
				case Command.Info:
					await Console.Out.WriteLineAsync(await checker.Info().ConfigureAwait(false)).ConfigureAwait(false);
					break;
				case Command.Check:
					await checker.Check(args.Host).ConfigureAwait(false);
					break;
				case Command.Put:
					await Console.Out.WriteLineAsync(await checker.Put(args.Host, args.Id, args.Flag, args.Vuln).ConfigureAwait(false)).ConfigureAwait(false);
					break;
				case Command.Get:
					await checker.Get(args.Host, args.Id, args.Flag, args.Vuln).ConfigureAwait(false);
					break;
				default:
					throw new CheckerException(ExitCode.CHECKER_ERROR, "Unknown command");
			}
		}

		private static async Task Debug(IChecker checker, string host)
		{
			for(int i = 0; i < int.MaxValue; i++)
			{
				try
				{
					var vulns = (await checker.Info().ConfigureAwait(false)).Split(':').Skip(1).Select(v => int.Parse(v.Trim())).ToArray();
					await checker.Check(host).ConfigureAwait(false);

					var vuln = RndDbg.RandomVuln(vulns);
					var flag = RndDbg.RandomFlag();

					var flagid = await checker.Put(host, "", flag, vuln).ConfigureAwait(false);
					await checker.Get(host, flagid, flag, vuln).ConfigureAwait(false);

					Console.ForegroundColor = ConsoleColor.Green;
					await Console.Error.WriteLineAsync(ExitCode.OK.ToString()).ConfigureAwait(false);
					Console.ResetColor();
				}
				catch(CheckerException e)
				{
					await Console.Error.WriteLineAsync(e.ExitCode.ToString()).ConfigureAwait(false);
					return;
				}
			}
		}

		private static CheckerArgs ParseArgs(string[] args)
		{
			if(args.Length == 0)
				throw new CheckerException(ExitCode.CHECKER_ERROR, "Not enough arguments");
			Command command;
			if(!Enum.TryParse(args[0], true, out command) || !Enum.IsDefined(typeof(Command), command))
				throw new CheckerException(ExitCode.CHECKER_ERROR, "Unknown command");
			if(command == Command.Info)
				return new CheckerArgs {Command = command};
			if(args.Length == 1)
				throw new CheckerException(ExitCode.CHECKER_ERROR, "Not enough arguments");
			if(command == Command.Check || command == Command.Debug)
				return new CheckerArgs {Command = command, Host = args[1]};
			if(args.Length < 5)
				throw new CheckerException(ExitCode.CHECKER_ERROR, "Not enough arguments");
			int vuln;
			if(!int.TryParse(args[4], out vuln))
				throw new CheckerException(ExitCode.CHECKER_ERROR, "Invalid vuln");
			return new CheckerArgs {Command = command, Host = args[1], Id = args[2], Flag = args[3], Vuln = vuln};
		}

		private class CheckerArgs
		{
			public Command Command;
			public string Host;
			public string Id;
			public string Flag;
			public int Vuln;
		}
	}
}
