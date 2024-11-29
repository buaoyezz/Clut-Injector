#include <Windows.h>
#include <vector>
#include <cstring> 
#include <iostream>

extern "C" __declspec(dllexport) bool InjectDLL(DWORD processID, const char* dllPath) {
    HANDLE hProcess = OpenProcess(PROCESS_CREATE_THREAD | PROCESS_QUERY_INFORMATION | PROCESS_VM_OPERATION | PROCESS_VM_WRITE | PROCESS_VM_READ, FALSE, processID);
    if (!hProcess) {
        DWORD error = GetLastError();
        std::cerr << "Failed to open process. Error: " << error << std::endl;
        return false;
    }

    LPVOID pRemoteMemory = VirtualAllocEx(hProcess, NULL, strlen(dllPath) + 1, MEM_COMMIT, PAGE_READWRITE);
    if (!pRemoteMemory) {
        DWORD error = GetLastError();
        std::cerr << "Failed to allocate memory in remote process. Error: " << error << std::endl;
        CloseHandle(hProcess);
        return false;
    }

    SIZE_T written;
    if (!WriteProcessMemory(hProcess, pRemoteMemory, dllPath, strlen(dllPath) + 1, &written)) {
        DWORD error = GetLastError();
        std::cerr << "Failed to write memory in remote process. Error: " << error << std::endl;
        VirtualFreeEx(hProcess, pRemoteMemory, 0, MEM_RELEASE);
        CloseHandle(hProcess);
        return false;
    }

    HMODULE hKernel32 = GetModuleHandleA("kernel32.dll");
    LPVOID pLoadLibraryA = GetProcAddress(hKernel32, "LoadLibraryA");
    if (!pLoadLibraryA) {
        std::cerr << "Failed to get address of LoadLibraryA." << std::endl;
        VirtualFreeEx(hProcess, pRemoteMemory, 0, MEM_RELEASE);
        CloseHandle(hProcess);
        return false;
    }

    HANDLE hThread = CreateRemoteThread(hProcess, NULL, 0, (LPTHREAD_START_ROUTINE)pLoadLibraryA, pRemoteMemory, 0, NULL);
    if (!hThread) {
        DWORD error = GetLastError();
        std::cerr << "Failed to create remote thread. Error: " << error << std::endl;
        VirtualFreeEx(hProcess, pRemoteMemory, 0, MEM_RELEASE);
        CloseHandle(hProcess);
        return false;
    }

    WaitForSingleObject(hThread, INFINITE);

    DWORD exitCode;
    if (GetExitCodeThread(hThread, &exitCode) && exitCode == 0) {
        std::cerr << "Remote thread failed with exit code 0." << std::endl;
        VirtualFreeEx(hProcess, pRemoteMemory, 0, MEM_RELEASE);
        CloseHandle(hThread);
        CloseHandle(hProcess);
        return false;
    }

    VirtualFreeEx(hProcess, pRemoteMemory, 0, MEM_RELEASE);
    CloseHandle(hThread);
    CloseHandle(hProcess);

    return true;
}
