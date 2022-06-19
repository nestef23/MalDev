using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Text;


class Program
{
	[DllImport("Dnsapi.dll", EntryPoint = "DnsQuery_W", ExactSpelling = true,
		CharSet = CharSet.Unicode, SetLastError = true)]
	static extern int DnsQuery(string lpstrName, short wType, int options,
		IntPtr pExtra, ref IntPtr ppQueryResultsSet, IntPtr pReserved);

	[DllImport("Dnsapi.dll")]
	static extern void DnsRecordListFree(IntPtr pRecordList, int freeType);

	[StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
	struct DnsRecordTxt
	{
		public IntPtr pNext;
		public string pName;
		public short wType;
		public short wDataLength;
		public int flags;
		public int dwTtl;
		public int dwReserved;
		public int dwStringCount;
		public string pStringArray;
	}

	enum DNS_FREE_TYPE
	{
		DnsFreeFlat = 0,
		DnsFreeRecordList = 1,
		DnsFreeParsedMessageFields = 2
	}

	static void Main(string[] args)
	{
		short DNS_TYPE_TEXT = 0x0010;
		int DNS_QUERY_STANDARD = 0x00000000;
		int DNS_ERROR_RCODE_NAME_ERROR = 9003;
		int DNS_INFO_NO_RECORDS = 9501;

		//Pass domain to query as first argument
		string domain = "google.com";
		if (args.Length > 0)
			domain = args[0];

		var queryResultsSet = IntPtr.Zero;
		DnsRecordTxt dnsRecord;
		var dnsStatus = DnsQuery(
				domain,
				DNS_TYPE_TEXT,
				DNS_QUERY_STANDARD,
				IntPtr.Zero,
				ref queryResultsSet,
				IntPtr.Zero
			);
		if (dnsStatus == DNS_ERROR_RCODE_NAME_ERROR
			|| dnsStatus == DNS_INFO_NO_RECORDS)
		{
			Console.WriteLine("no records or DNS lookup failed");
		}
		// throw an exception if other non success code
		if (dnsStatus != 0)
			throw new Win32Exception(dnsStatus);

		// step through each result
		for (
			var pointer = queryResultsSet;
			pointer != IntPtr.Zero;
			pointer = dnsRecord.pNext)
		{
			dnsRecord = (DnsRecordTxt)
				Marshal.PtrToStructure(pointer, typeof(DnsRecordTxt));

			if (dnsRecord.wType == DNS_TYPE_TEXT)
			{
				var builder = new StringBuilder();

				// pointer to array of pointers
				// to each string that makes up the record
				var stringArrayPointer = pointer + Marshal.OffsetOf(
					typeof(DnsRecordTxt), "pStringArray").ToInt32();

				// concatenate multiple strings in the case of long records
				for (var i = 0; i < dnsRecord.dwStringCount; ++i)
				{
					var stringPointer = (IntPtr)Marshal.PtrToStructure(
						stringArrayPointer, typeof(IntPtr));

					builder.Append(Marshal.PtrToStringUni(stringPointer));
					stringArrayPointer += IntPtr.Size;
				}

				Console.WriteLine(builder.ToString());
			}
		}
	}
}
