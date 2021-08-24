using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using svghost.utils;

namespace svghost
{
	public struct Svg
	{
		public DateTime Date { get; set; }
		public Guid UserId { get; set; }
		public Guid FileId { get; set; }
		public bool IsPrivate { get; set; }
	}

	public static class SvgStore
	{
		static SvgStore()
		{
			foreach(var svg in ListFiles())
				Svgs.AddFirst(svg);
			CleanupTimer = new Timer(_ =>
			{
				ReadSafeLinkedListNode<Svg> head;
				var border = DateTime.UtcNow.AddMinutes(-SvgTtlMinutes);
				while((head = Svgs.Last) != null && head.Value.Date < border)
					lock(Svgs) Svgs.RemoveLast();
			}, null, 60000, 60000);
		}

		public static async Task SaveAsync(Guid userId, Guid fileId, bool isPrivate, string data, string sanitized)
		{
			var utcNow = DateTime.UtcNow;
			var dir = Path.Combine(DataDirectory, RollingValue(utcNow).ToString(NumberFormatInfo.InvariantInfo));
			Directory.CreateDirectory(dir);
			await SaveAsync(dir, userId, fileId, isPrivate, data, false);
			await SaveAsync(dir, userId, fileId, isPrivate, sanitized, true);
			lock(Svgs) Svgs.AddFirst(new Svg {Date = utcNow, UserId = userId, FileId = fileId, IsPrivate = isPrivate});
		}

		private static async Task SaveAsync(string dir, Guid userId, Guid fileId, bool isPrivate, string data, bool sanitized)
		{
			var path = Path.Combine(dir, ToFilename(userId, fileId, isPrivate, sanitized));
			var tmp = path + TmpFileExtension;
			await File.WriteAllTextAsync(tmp, data);
			File.Move(tmp, path, true);
		}

		public static IEnumerable<Svg> List()
			=> Svgs.AsEnumerable();

		private static IEnumerable<Svg> ListFiles() => LastRollingFolders()
			.SelectMany(rolling =>
			{
				try { return Directory.EnumerateFiles(Path.Combine(DataDirectory, rolling), "*-true.svg"); }
				catch(DirectoryNotFoundException) { return Array.Empty<string>(); }
			})
			.Select(file => (file, time: File.GetCreationTimeUtc(file)))
			.OrderBy(item => item.time)
			.Select(item => ParseFileName(item.file, item.time))
			.Where(item => !item.Equals(default));

		public static string FindFilePath(Guid userId, Guid fileId, bool isPrivate, bool sanitized)
			=> LastRollingFolders().Select(rolling => Path.Combine(DataDirectory, rolling, ToFilename(userId, fileId, isPrivate, sanitized))).FirstOrDefault(File.Exists);

		public static async Task<string> FindDataAsync(Guid userId, Guid fileId, bool isPrivate, bool sanitized)
		{
			var filepath = FindFilePath(userId, fileId, isPrivate, sanitized);
			if(filepath == null)
				return null;

			try { return await File.ReadAllTextAsync(filepath); }
			catch(DirectoryNotFoundException) { return null; }
			catch(FileNotFoundException) { return null; }
		}

		private static string ToFilename(Guid userId, Guid fileId, bool isPrivate, bool sanitized)
			=> $"{userId:N}-{fileId:N}-{isPrivate}-{sanitized}{FileExtension}".ToLowerInvariant();

		private static Svg ParseFileName(string filepath, DateTime time)
		{
			var parts = Path.GetFileNameWithoutExtension(filepath).Split('-');
			if(parts.Length != 4)
				return default;
			if(!(Guid.TryParseExact(parts[0], "N", out var userId) && Guid.TryParseExact(parts[1], "N", out var fileId) && bool.TryParse(parts[2], out var isPrivate) && bool.TryParse(parts[3], out _)))
				return default;
			return new Svg {UserId = userId, FileId = fileId, Date = time, IsPrivate = isPrivate};
		}

		private static IEnumerable<string> LastRollingFolders()
		{
			var utcNow = DateTime.UtcNow;
			for(int i = LastRollingFoldersToCheck; i >= 0; i--)
				yield return RollingValue(utcNow.AddTicks(-i * 10L * 60L * 10000000L)).ToString(NumberFormatInfo.InvariantInfo);
		}

		private static long RollingValue(DateTime utcNow)
			=> utcNow.Year * 10000000L + utcNow.Month * 100000L + utcNow.Day * 1000L + utcNow.Hour * 10L + utcNow.Minute / 10;

		private const string DataDirectory = "data";
		private const string FileExtension = ".svg";
		private const string TmpFileExtension = ".tmp";

		private const int SvgTtlMinutes = 30;
		private const int LastRollingFoldersToCheck = 3;

		private static readonly ReadSafeLinkedListNode<Svg>.LinkedList Svgs = new();
		private static readonly Timer CleanupTimer;
	}
}
