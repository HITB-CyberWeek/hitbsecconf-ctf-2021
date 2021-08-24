using System.Threading.Tasks;

namespace checker
{
	internal interface IChecker
	{
		Task<string> Info();
		Task Check(string host);
		Task<string> Put(string host, string id, string flag, int vuln);
		Task Get(string host, string id, string flag, int vuln);
	}
}
