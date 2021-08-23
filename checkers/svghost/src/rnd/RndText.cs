using System;
using System.Collections.Generic;
using System.Text;
using checker.utils;

namespace checker.rnd
{
	internal static class RndText
	{
		private static readonly string[] Bigrams =
		{
			"TH", "OF", "AN", "IN", "TO", "CO", "BE", "HE", "RE", "HA", "WA", "FO", "WH", "MA", "WI", "ON", "HI", "PR", "ST",
			"NO", "IS", "IT", "SE", "WE", "AS", "CA", "DE", "SO", "MO", "SH", "DI", "AL", "AR", "LI", "WO", "FR", "PA", "ME",
			"AT", "SU", "BU", "SA", "FI", "NE", "CH", "PO", "HO", "DO", "OR", "UN", "LO", "EX", "BY", "FA", "LA", "LE", "PE",
			"MI", "SI", "YO", "TR", "BA", "GO", "BO", "GR", "TE", "EN", "OU", "RA", "AC", "FE", "PL", "CL", "SP", "BR", "EV",
			"TA", "DA", "AB", "TI", "RO", "MU", "EA", "NA", "SC", "AD", "GE", "YE", "AF", "AG", "UP", "AP", "DR", "US", "PU",
			"CE", "IF", "RI", "VI", "IM", "AM", "KN", "OP", "CR", "OT", "JU", "QU", "TW", "GA", "VA", "VE", "PI", "GI", "BI",
			"FL", "BL", "EL", "JO", "FU", "HU", "CU", "RU", "OV", "MY", "OB", "KE", "EF", "PH", "CI", "KI", "NI", "SL", "EM",
			"SM", "VO", "MR", "WR", "ES", "DU", "TU", "AU", "NU", "GU", "OW", "SY", "JA", "OC", "EC", "ED", "ID", "JE", "AI",
			"EI", "SK", "OL", "GL", "EQ", "LU", "AV", "SW", "AW", "EY", "TY"
		};

		private static readonly Dictionary<string, Tuple<string, string>> Trigrams = new Dictionary<string, Tuple<string, string>>(StringComparer.Ordinal)
		{
			{"TH", new Tuple<string, string>("EAIOR", "EO")},
			{"AN", new Tuple<string, string>("DTYCSGNIOEAK", "DTYSGOEAK")},
			{"IN", new Tuple<string, string>("GTEDSCAIKVUNF", "GTEDSAK")},
			{"IO", new Tuple<string, string>("NUR", "NUR")},
			{"EN", new Tuple<string, string>("TCDSEIGONA", "TDSEGOA")},
			{"TI", new Tuple<string, string>("ONCVMLETSARF", "NCMLETSARF")},
			{"FO", new Tuple<string, string>("RUOL", "RUOL")},
			{"HE", new Tuple<string, string>("RNYSMIALDT", "RNYSMALDT")},
			{"HA", new Tuple<string, string>("TDVNSRPL", "TDNSRL")},
			{"HI", new Tuple<string, string>("SNCMLPGTRE", "SNCMLPGTRE")},
			{"TE", new Tuple<string, string>("RDNSMLECA", "RDNSMLEA")},
			{"AT", new Tuple<string, string>("IETHUOC", "EHO")},
			{"ER", new Tuple<string, string>("ESIANYTVMROLGFC", "ESANYTM")},
			{"AL", new Tuple<string, string>("LSITEUOMKFA", "LSTEF")},
			{"WA", new Tuple<string, string>("SYRTNL", "SYRTNL")},
			{"VE", new Tuple<string, string>("RNLSD", "RNLSD")},
			{"CO", new Tuple<string, string>("NMURLVSO", "NMURLO")},
			{"RE", new Tuple<string, string>("SADNECLTPMVGFQ", "SADNELTPM")},
			{"IT", new Tuple<string, string>("HIYESTAU", "HYESA")},
			{"WI", new Tuple<string, string>("TLNS", "TLNS")},
			{"ME", new Tuple<string, string>("NRDTSMA", "NRDTSMA")},
			{"NC", new Tuple<string, string>("EIHTROL", "EHT")},
			{"ON", new Tuple<string, string>("SETGADLCVOIF", "SETGADO")},
			{"PR", new Tuple<string, string>("OEIA", "EA")},
			{"AR", new Tuple<string, string>("ETDYSIRLMKGAONC", "ETDYSMKAN")},
			{"ES", new Tuple<string, string>("STEIPUC", "STE")},
			{"EV", new Tuple<string, string>("EI", "E")},
			{"ST", new Tuple<string, string>("ARIEOUS", "AEOS")},
			{"EA", new Tuple<string, string>("RSTDLCNVMK", "RSTDLNM")},
			{"IV", new Tuple<string, string>("EIA", "E")},
			{"EC", new Tuple<string, string>("TOIEAURH", "TEH")},
			{"NO", new Tuple<string, string>("TWRUNM", "TWRUNM")},
			{"OU", new Tuple<string, string>("TLRNSGPB", "TLRNSP")},
			{"PE", new Tuple<string, string>("RNCADTO", "RNADT")},
			{"IL", new Tuple<string, string>("LEIYDA", "LEYD")},
			{"IS", new Tuple<string, string>("THSIECM", "THSEM")},
			{"MA", new Tuple<string, string>("NTLKDSIG", "NTLDS")},
			{"AV", new Tuple<string, string>("EIA", "E")},
			{"OM", new Tuple<string, string>("EPMIA", "E")},
			{"IC", new Tuple<string, string>("AHEITKUS", "HETKS")},
			{"GH", new Tuple<string, string>("T", "T")},
			{"DE", new Tuple<string, string>("RNSDAVPTMLF", "RNSDAPTML")},
			{"AI", new Tuple<string, string>("NDRLT", "NDRLT")},
			{"CT", new Tuple<string, string>("IEUSO", "ESO")},
			{"IG", new Tuple<string, string>("HNI", "HN")},
			{"ID", new Tuple<string, string>("E", "E")},
			{"OR", new Tuple<string, string>("ETMDSKIYLGARNC", "ETMDSKYAN")},
			{"OV", new Tuple<string, string>("EI", "E")},
			{"UL", new Tuple<string, string>("DTAL", "DTL")},
			{"YO", new Tuple<string, string>("U", "U")},
			{"BU", new Tuple<string, string>("TSRI", "TSR")},
			{"RA", new Tuple<string, string>("TNLCIMDSRPGB", "TNLMDSR")},
			{"FR", new Tuple<string, string>("OEA", "EA")},
			{"RO", new Tuple<string, string>("MUVPNWSOLDCBATG", "MUPNWOLDT")},
			{"WH", new Tuple<string, string>("IEOA", "EO")},
			{"OT", new Tuple<string, string>("HETI", "HE")},
			{"BL", new Tuple<string, string>("EIYOA", "EY")},
			{"NT", new Tuple<string, string>("EISROALYUH", "ESOAYH")},
			{"UN", new Tuple<string, string>("DTICG", "DTG")},
			{"TR", new Tuple<string, string>("AIOEUY", "AEY")},
			{"HO", new Tuple<string, string>("UWSRLOMTPND", "UWRLOMTPND")},
			{"AC", new Tuple<string, string>("TEKHCRI", "TEKH")},
			{"TU", new Tuple<string, string>("RDAT", "RT")},
			{"WE", new Tuple<string, string>("RLEVSNA", "RLESNA")},
			{"CA", new Tuple<string, string>("LNTRUSMP", "LNTRSM")},
			{"SH", new Tuple<string, string>("EOIA", "EO")},
			{"UR", new Tuple<string, string>("ENTSIAYRPC", "ENTSAY")},
			{"IE", new Tuple<string, string>("SNDTWVRLF", "SNDTWRL")},
			{"PA", new Tuple<string, string>("RTSNLIC", "RTSNL")},
			{"TO", new Tuple<string, string>("RONWPML", "RONWPML")},
			{"EE", new Tuple<string, string>("NDTMSRPLK", "NDTMSRPLK")},
			{"LI", new Tuple<string, string>("NTSCKGEFZVOMA", "NTSCGEFMA")},
			{"RI", new Tuple<string, string>("NECTSGAVOPMLDB", "NECTSGAPMLD")},
			{"UG", new Tuple<string, string>("HG", "H")},
			{"AM", new Tuple<string, string>("EPIOA", "E")},
			{"ND", new Tuple<string, string>("EISAUO", "ESO")},
			{"US", new Tuple<string, string>("ETISLH", "ETSH")},
			{"LL", new Tuple<string, string>("YEOISA", "YES")},
			{"AS", new Tuple<string, string>("TSEIUOKH", "TSEOH")},
			{"TA", new Tuple<string, string>("TNLIRKBGC", "TNLR")},
			{"LE", new Tuple<string, string>("SDATCRNMGVF", "SDATRNM")},
			{"MO", new Tuple<string, string>("RSVTUD", "RTUD")},
			{"WO", new Tuple<string, string>("RU", "RU")},
			{"MI", new Tuple<string, string>("NLSTCG", "NLSTCG")},
			{"AB", new Tuple<string, string>("LOI", "")},
			{"EL", new Tuple<string, string>("LYIEFOATSPD", "LYEFTSD")},
			{"IA", new Tuple<string, string>("LNT", "LNT")},
			{"NA", new Tuple<string, string>("LTRNM", "LTRNM")},
			{"SS", new Tuple<string, string>("IEUOA", "EO")},
			{"AG", new Tuple<string, string>("EAO", "EO")},
			{"TT", new Tuple<string, string>("ELI", "E")},
			{"NE", new Tuple<string, string>("DSWREYVTLCA", "DSWREYTLA")},
			{"PL", new Tuple<string, string>("AEIYO", "EY")},
			{"LA", new Tuple<string, string>("TNRSCYWIB", "TNRSYW")},
			{"OS", new Tuple<string, string>("TESI", "TES")},
			{"CE", new Tuple<string, string>("SNRDPLI", "SNRDPL")},
			{"DI", new Tuple<string, string>("SNTDFECAVR", "SNTDFECAR")},
			{"BE", new Tuple<string, string>("RECTLFSIGDA", "RETLSDA")},
			{"AP", new Tuple<string, string>("PEA", "E")},
			{"SI", new Tuple<string, string>("ONDTSGCBVMA", "NDTSGCMA")},
			{"NI", new Tuple<string, string>("NTSCZOGF", "NTSCGF")},
			{"OW", new Tuple<string, string>("NESIA", "NES")},
			{"SO", new Tuple<string, string>("NMULCR", "NMULR")},
			{"AK", new Tuple<string, string>("EI", "E")},
			{"CH", new Tuple<string, string>("EAIOUR", "EO")},
			{"EM", new Tuple<string, string>("ESPOBAI", "ES")},
			{"IM", new Tuple<string, string>("EPIASM", "ES")},
			{"SE", new Tuple<string, string>("DNLSRECTVA", "DNLSRETA")},
			{"NS", new Tuple<string, string>("TIE", "TE")},
			{"PO", new Tuple<string, string>("SRNLWTI", "RNLWT")},
			{"EI", new Tuple<string, string>("RNGT", "RNGT")},
			{"EX", new Tuple<string, string>("PTICA", "T")},
			{"KI", new Tuple<string, string>("N", "N")},
			{"UC", new Tuple<string, string>("HTKE", "HTKE")},
			{"AD", new Tuple<string, string>("EIYVMD", "EY")},
			{"GR", new Tuple<string, string>("EAO", "EA")},
			{"IR", new Tuple<string, string>("ESTLI", "EST")},
			{"NG", new Tuple<string, string>("ESLTRI", "ES")},
			{"OP", new Tuple<string, string>("EPL", "E")},
			{"SP", new Tuple<string, string>("EOIA", "E")},
			{"OL", new Tuple<string, string>("DLIOEU", "DLE")},
			{"DA", new Tuple<string, string>("YTRN", "YTRN")},
			{"NL", new Tuple<string, string>("Y", "Y")},
			{"TL", new Tuple<string, string>("YE", "YE")},
			{"LO", new Tuple<string, string>("WNOSCVUTRPG", "WNOUTRP")},
			{"BO", new Tuple<string, string>("UTRODA", "UTROD")},
			{"RS", new Tuple<string, string>("TEOI", "TEO")},
			{"FE", new Tuple<string, string>("REWLCA", "REWLA")},
			{"FI", new Tuple<string, string>("RNCELG", "RNCELG")},
			{"SU", new Tuple<string, string>("RCPBMLA", "RPML")},
			{"GE", new Tuple<string, string>("NTSRD", "NTSRD")},
			{"MP", new Tuple<string, string>("LOATRE", "TE")},
			{"UA", new Tuple<string, string>("LTR", "LTR")},
			{"OO", new Tuple<string, string>("KDLTRNM", "KDLTRNM")},
			{"RT", new Tuple<string, string>("IHAEYUS", "HAEYS")},
			{"SA", new Tuple<string, string>("IMYNL", "MYNL")},
			{"CR", new Tuple<string, string>("EIOA", "EA")},
			{"FF", new Tuple<string, string>("EI", "E")},
			{"IK", new Tuple<string, string>("E", "E")},
			{"MB", new Tuple<string, string>("E", "E")},
			{"KE", new Tuple<string, string>("DNTSRE", "DNTSRE")},
			{"FA", new Tuple<string, string>("CRMI", "RM")},
			{"CI", new Tuple<string, string>("ATESPN", "ATESPN")},
			{"EQ", new Tuple<string, string>("U", "")},
			{"AF", new Tuple<string, string>("TF", "TF")},
			{"ET", new Tuple<string, string>("TIHEYWSA", "HEYSA")},
			{"AY", new Tuple<string, string>("SE", "S")},
			{"MU", new Tuple<string, string>("SNLC", "SNL")},
			{"UE", new Tuple<string, string>("SN", "SN")},
			{"HR", new Tuple<string, string>("OEI", "E")},
			{"TW", new Tuple<string, string>("OE", "OE")},
			{"GI", new Tuple<string, string>("NVOC", "NC")},
			{"OI", new Tuple<string, string>("N", "N")},
			{"VI", new Tuple<string, string>("NDSCTOLE", "NDSCTLE")},
			{"CU", new Tuple<string, string>("LRTS", "LRTS")},
			{"FU", new Tuple<string, string>("LRN", "LRN")},
			{"ED", new Tuple<string, string>("IUE", "E")},
			{"QU", new Tuple<string, string>("IEA", "E")},
			{"UT", new Tuple<string, string>("IHE", "HE")},
			{"RC", new Tuple<string, string>("HE", "HE")},
			{"OF", new Tuple<string, string>("FT", "FT")},
			{"CL", new Tuple<string, string>("EAUO", "E")},
			{"FT", new Tuple<string, string>("E", "E")},
			{"IZ", new Tuple<string, string>("EA", "E")},
			{"PP", new Tuple<string, string>("EORL", "E")},
			{"RG", new Tuple<string, string>("EA", "E")},
			{"DU", new Tuple<string, string>("CSRA", "SR")},
			{"RM", new Tuple<string, string>("ASIE", "SE")},
			{"YE", new Tuple<string, string>("ASD", "ASD")},
			{"RL", new Tuple<string, string>("YD", "YD")},
			{"DO", new Tuple<string, string>("WNME", "WNM")},
			{"AU", new Tuple<string, string>("TS", "TS")},
			{"EP", new Tuple<string, string>("TOEA", "TE")},
			{"BA", new Tuple<string, string>("SCRNL", "SRNL")},
			{"JU", new Tuple<string, string>("S", "S")},
			{"RD", new Tuple<string, string>("SEI", "SE")},
			{"RU", new Tuple<string, string>("SNC", "SN")},
			{"OG", new Tuple<string, string>("RI", "")},
			{"BR", new Tuple<string, string>("OIEA", "EA")},
			{"EF", new Tuple<string, string>("OFUTE", "FTE")},
			{"KN", new Tuple<string, string>("OE", "OE")},
			{"LS", new Tuple<string, string>("O", "O")},
			{"GA", new Tuple<string, string>("NITR", "NTR")},
			{"PI", new Tuple<string, string>("NTREC", "NTREC")},
			{"YI", new Tuple<string, string>("N", "N")},
			{"BI", new Tuple<string, string>("LTN", "LTN")},
			{"IB", new Tuple<string, string>("LIE", "E")},
			{"UB", new Tuple<string, string>("L", "")},
			{"VA", new Tuple<string, string>("LTRN", "LTRN")},
			{"OC", new Tuple<string, string>("KIECA", "KE")},
			{"IF", new Tuple<string, string>("IFET", "FET")},
			{"RN", new Tuple<string, string>("IEMA", "EA")},
			{"RR", new Tuple<string, string>("IEYO", "EY")},
			{"SC", new Tuple<string, string>("HROIA", "H")},
			{"TC", new Tuple<string, string>("H", "H")},
			{"CK", new Tuple<string, string>("E", "E")},
			{"DG", new Tuple<string, string>("E", "E")},
			{"DR", new Tuple<string, string>("EOIA", "EA")},
			{"MM", new Tuple<string, string>("EUI", "E")},
			{"NN", new Tuple<string, string>("EOI", "EO")},
			{"OD", new Tuple<string, string>("EYU", "EY")},
			{"RV", new Tuple<string, string>("EI", "E")},
			{"UD", new Tuple<string, string>("EI", "E")},
			{"XP", new Tuple<string, string>("E", "E")},
			{"JE", new Tuple<string, string>("C", "")},
			{"UM", new Tuple<string, string>("BE", "E")},
			{"EG", new Tuple<string, string>("ARIE", "E")},
			{"DL", new Tuple<string, string>("YE", "YE")},
			{"PH", new Tuple<string, string>("YOIE", "YOE")},
			{"SL", new Tuple<string, string>("YA", "Y")},
			{"GO", new Tuple<string, string>("VTO", "TO")},
			{"CC", new Tuple<string, string>("UOE", "E")},
			{"LU", new Tuple<string, string>("TSMED", "TSME")},
			{"OA", new Tuple<string, string>("TRD", "TRD")},
			{"PU", new Tuple<string, string>("TRLB", "TRL")},
			{"UI", new Tuple<string, string>("TRL", "TRL")},
			{"YS", new Tuple<string, string>("T", "T")},
			{"ZA", new Tuple<string, string>("T", "T")},
			{"HU", new Tuple<string, string>("SRNM", "SRNM")},
			{"MR", new Tuple<string, string>("S", "S")},
			{"OE", new Tuple<string, string>("S", "S")},
			{"SY", new Tuple<string, string>("S", "S")},
			{"EO", new Tuple<string, string>("RP", "RP")},
			{"TY", new Tuple<string, string>("P", "")},
			{"UP", new Tuple<string, string>("PO", "")},
			{"FL", new Tuple<string, string>("OE", "E")},
			{"LM", new Tuple<string, string>("O", "")},
			{"NF", new Tuple<string, string>("O", "")},
			{"RP", new Tuple<string, string>("O", "")},
			{"OH", new Tuple<string, string>("N", "")},
			{"NU", new Tuple<string, string>("M", "M")},
			{"XA", new Tuple<string, string>("M", "M")},
			{"OB", new Tuple<string, string>("L", "")},
			{"VO", new Tuple<string, string>("L", "L")},
			{"DM", new Tuple<string, string>("I", "")},
			{"GN", new Tuple<string, string>("I", "")},
			{"LD", new Tuple<string, string>("IE", "E")},
			{"PT", new Tuple<string, string>("I", "")},
			{"SK", new Tuple<string, string>("IE", "E")},
			{"WR", new Tuple<string, string>("I", "")},
			{"JO", new Tuple<string, string>("H", "")},
			{"LT", new Tuple<string, string>("HE", "HE")},
			{"YT", new Tuple<string, string>("H", "H")},
			{"UF", new Tuple<string, string>("F", "F")},
			{"BJ", new Tuple<string, string>("E", "")},
			{"DD", new Tuple<string, string>("E", "E")},
			{"EY", new Tuple<string, string>("E", "")},
			{"GG", new Tuple<string, string>("E", "E")},
			{"GL", new Tuple<string, string>("EA", "E")},
			{"GU", new Tuple<string, string>("E", "E")},
			{"HT", new Tuple<string, string>("E", "E")},
			{"LV", new Tuple<string, string>("E", "E")},
			{"MS", new Tuple<string, string>("E", "E")},
			{"NM", new Tuple<string, string>("E", "E")},
			{"NV", new Tuple<string, string>("E", "E")},
			{"OK", new Tuple<string, string>("E", "E")},
			{"PM", new Tuple<string, string>("E", "E")},
			{"RK", new Tuple<string, string>("E", "E")},
			{"SW", new Tuple<string, string>("E", "E")},
			{"TM", new Tuple<string, string>("E", "E")},
			{"XC", new Tuple<string, string>("E", "E")},
			{"ZE", new Tuple<string, string>("D", "D")},
			{"AW", new Tuple<string, string>("A", "")},
			{"SM", new Tuple<string, string>("A", "")}
		};

		public static string RandomText(int n)
		{
			if(n <= 0) return string.Empty;
			var builder = new StringBuilder(n);
			while(builder.Length < n)
			{
				builder.Append(RandomWord(RndUtil.GetInt(2, 10)));
				builder.Append(' ');
			}
			builder.Length = n;
			builder[0] = char.ToUpper(builder[0]);
			return builder.ToString();
		}

		public static string RandomWord(int n)
		{
			var lookup = new char[2];
			var builder = new StringBuilder(n);
			while(builder.Length < n)
			{
				if(builder.Length < 2)
				{
					builder.Append(RndUtil.Choice(Bigrams));
					continue;
				}

				lookup[0] = builder[builder.Length - 2];
				lookup[1] = builder[builder.Length - 1];

				var bigram = new string(lookup);
				var candidates = builder.Length == n - 1 ? Trigrams.GetOrDefault(bigram)?.Item2 : Trigrams.GetOrDefault(bigram)?.Item1;

				if(candidates?.Length > 0)
					builder.Append(RndUtil.Choice(candidates));
				else
					builder.Length = Math.Max(0, builder.Length - 3);
			}
			return builder.ToString().ToLower();
		}

		public static string RandomUpperCase(this string value)
		{
			var chars = value.ToCharArray();
			for(int i = 0; i < chars.Length; i++)
			{
				if(RndUtil.ThreadStaticRnd.Next(4) == 0)
					chars[i] = char.ToUpperInvariant(chars[i]);
			}
			return new string(chars);
		}

		public static string RandomUmlauts(this string value)
			=> RandomChangeByDict(value, Umlauts, 16);
		public static string RandomLeet(this string value)
			=> RandomChangeByDict(value, Leet, 4);
		public static string RandomChangeByDict(this string value, Dictionary<char, char> dict, int share)
		{
			var chars = value.ToCharArray();
			for(int i = 0; i < chars.Length; i++)
			{
				if(dict.TryGetValue(chars[i], out var c) && RndUtil.ThreadStaticRnd.Next(share) == 0)
					chars[i] = c;
			}
			return new string(chars);
		}

		private static readonly Dictionary<char, char> Leet = new Dictionary<char, char>
		{
			{'o', '0'},
			{'l', '1'},
			{'e', '3'},
			{'t', '7'},
		};

		private static readonly Dictionary<char, char> Umlauts = new Dictionary<char, char>
		{
			{'s', 'ß'},
			{'o', 'ö'},
			{'u', 'ü'},
			{'e', 'ë'},
			{'a', 'â'},
			{'z', 'ž'},
			{'n', 'ň'},
			{'y', 'ý'},
		};
	}
}
