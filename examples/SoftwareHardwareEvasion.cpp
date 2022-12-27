// Based on https://anti-reversing.com/Downloads/Anti-Reversing/The_Ultimate_Anti-Reversing_Reference.pdf
// and https://evasions.checkpoint.com/techniques/cpu.html
#include <iostream>
#include <intrin.h>
#include <string>
#include <fileapi.h>
#include <cstdio>
#include <memory>
#include <stdexcept>
#include <string>
#include <array>

int main()
{
    // ------ CHECK CPU ----------
    std::cout << "Check 1" << std::endl;
    // x86 registry values will be stored here
    uint32_t regs[4];
    // Running cpuid with eax=0 will return the processor's manufacture string
    __cpuid((int *)regs, (int)0);
    std::cout << "CPUID manufacturer ID" << std::endl;
    //EBX, EDX, ECX values
    std::string manufacturerID;
    manufacturerID = std::string((const char *)&regs[1],4);
    manufacturerID += std::string((const char *)&regs[3],4);
    manufacturerID += std::string((const char *)&regs[2],4);
    std::cout << manufacturerID << std::endl;
    if (manufacturerID != "AuthenticAMD" and manufacturerID != "GenuineIntel")
        std::cout << "Detected suspicious CPU!" << std::endl;

    // --------- CHECK baseboard product ---------
    std::cout << "Check 2" << std::endl;
    const char* cmd = "wmic baseboard get product, manufacturer";
    std::array<char, 128> buffer;
    std::string result;
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd, "r"), pclose);
    if (!pipe) {
        throw std::runtime_error("popen() failed!");
    }
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }
    std::cout << result << std::endl;
    if (strstr(result.c_str(),"VirtualBox"))
        std::cout << "VM detected!" << std::endl;
}