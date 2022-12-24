// Based on https://anti-reversing.com/Downloads/Anti-Reversing/The_Ultimate_Anti-Reversing_Reference.pdf
#include <iostream>
#include <windows.h>
#include <stdio.h>
#include <tlhelp32.h>

int main()
{
        // ------ CHECK DEBUGGER PRESENT ----------
    std::cout << "Running check 1 \n";

    //Check local debugger presence
    if (IsDebuggerPresent())
        std::cout << "Debugger detected - IsDebuggerPresent()\n";

    // Get process handle to itself
    HANDLE myproc =  GetCurrentProcess();
    // Check Remote Debugger Presence
    PBOOL RemoteDebuggerPresent = 0;
    CheckRemoteDebuggerPresent(myproc, RemoteDebuggerPresent);
    if (RemoteDebuggerPresent)
        std::cout << "Debugger detected - CheckRemoteDebuggerPresent()\n";

    // ------ CHECK PARENT PROCESS NAME --------
    std::cout << "Running check 2 \n";

    // Get handle to snapshot of all processes 
    HANDLE hsnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    
    // setup ID and name variables
    int pid = GetCurrentProcessId();
    int ppid = -1;
    int pppid = -1;
    char* PName;
    char* GPName;
    PName = (char*)malloc(260);
    GPName = (char*)malloc(260);
    
    // PROCESSENTRY32 structure.
    PROCESSENTRY32 pe = { 0 };
    pe.dwSize = sizeof(PROCESSENTRY32);
    
    // Iterate through the snapshot first time to get PPID
    if( Process32First(hsnap, &pe)) {
        do {
            if (pe.th32ProcessID == pid) {
                // Get PPID
                ppid = pe.th32ParentProcessID;
            }
        } while( Process32Next(hsnap, &pe));
    }
    
    // Iterate through the snapshot first time to get name of parent process (from PPID)
    if( Process32First(hsnap, &pe)) {
        do {
            if (pe.th32ProcessID == ppid) {
                std::cout <<"Parent process name: "<< pe.szExeFile <<"\n";
                strcpy(PName, pe.szExeFile);
                pppid = pe.th32ParentProcessID;
            }
        } while( Process32Next(hsnap, &pe));
    }
    
    // Iterate through the snapshot first time to get name of grandparent process (from PPPID)
    if( Process32First(hsnap, &pe)) {
        do {
            if (pe.th32ProcessID == pppid) {
                std::cout <<"Gparent process name: "<< pe.szExeFile <<"\n";
                strcpy(GPName, pe.szExeFile);
            }
        } while( Process32Next(hsnap, &pe));
    }
    
    // Check for anomalous process names
    if (strncmp(PName,"cmd.exe",8) != 0 and (strncmp(PName,"powershell.exe",15) != 0))
        std::cout <<"Suspicious parent detected: "<< PName <<"\n";
    if (strncmp(GPName,"cmd.exe",8) != 0 and (strncmp(GPName,"powershell.exe",15) != 0) and (strncmp(GPName,"explorer.exe",13) != 0))
        std::cout <<"Suspicious Gparent detected: "<< GPName <<"\n";
}