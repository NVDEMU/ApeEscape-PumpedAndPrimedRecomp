#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <commdlg.h>

#include <filesystem>
#include <string>
#include <vector>

static std::wstring quote_arg(const std::wstring &value) {
    std::wstring out = L"\"";
    unsigned slashes = 0;
    for (wchar_t ch : value) {
        if (ch == L'\\') {
            ++slashes;
        } else if (ch == L'"') {
            out.append(slashes * 2 + 1, L'\\');
            out.push_back(ch);
            slashes = 0;
        } else {
            out.append(slashes, L'\\');
            slashes = 0;
            out.push_back(ch);
        }
    }
    out.append(slashes * 2, L'\\');
    out.push_back(L'"');
    return out;
}

int WINAPI wWinMain(HINSTANCE, HINSTANCE, PWSTR, int) {
    wchar_t self[MAX_PATH] = {};
    const DWORD length = GetModuleFileNameW(nullptr, self, MAX_PATH);
    if (!length || length >= MAX_PATH) {
        MessageBoxW(nullptr, L"Could not locate the application folder.", L"Ape Escape: Pumped & Primed", MB_OK | MB_ICONERROR);
        return 1;
    }
    const std::filesystem::path gameDir = std::filesystem::path(self).parent_path();
    wchar_t iso[MAX_PATH] = {};
    OPENFILENAMEW dialog{};
    dialog.lStructSize = sizeof(dialog);
    dialog.lpstrFile = iso;
    dialog.nMaxFile = MAX_PATH;
    dialog.lpstrFilter = L"PlayStation 2 ISO images (*.iso)\0*.iso\0All files (*.*)\0*.*\0";
    dialog.lpstrTitle = L"Choose your Pumped & Primed ISO made from your own disc dump";
    dialog.Flags = OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST | OFN_NOCHANGEDIR;
    dialog.lpstrDefExt = L"iso";
    if (!GetOpenFileNameW(&dialog)) return 0;

    wchar_t appData[MAX_PATH] = {};
    const DWORD appDataLength = GetEnvironmentVariableW(L"APPDATA", appData, MAX_PATH);
    if (!appDataLength || appDataLength >= MAX_PATH) {
        MessageBoxW(nullptr, L"Could not locate your AppData folder.", L"Ape Escape: Pumped & Primed", MB_OK | MB_ICONERROR);
        return 1;
    }
    const std::filesystem::path saveDir = std::filesystem::path(appData) / L"Ape Escape Pumped and Primed Recomp";
    std::error_code ec;
    std::filesystem::create_directories(saveDir, ec);
    if (ec) {
        MessageBoxW(nullptr, L"Could not create the memory-card folder.", L"Ape Escape: Pumped & Primed", MB_OK | MB_ICONERROR);
        return 1;
    }

    const std::filesystem::path runner = gameDir / L"ps2run.exe";
    const std::filesystem::path elf = gameDir / L"SLUS_210.96";
    const std::filesystem::path card = saveDir / L"memorycard.ps2";
    std::wstring command = quote_arg(runner.wstring()) + L" " + quote_arg(elf.wstring()) +
        L" --disc " + quote_arg(iso) + L" --window --memcard " + quote_arg(card.wstring());
    std::vector<wchar_t> mutableCommand(command.begin(), command.end());
    mutableCommand.push_back(L'\0');

    STARTUPINFOW startup{};
    startup.cb = sizeof(startup);
    PROCESS_INFORMATION process{};
    if (!CreateProcessW(runner.c_str(), mutableCommand.data(), nullptr, nullptr, FALSE,
                        CREATE_NEW_CONSOLE, nullptr, gameDir.c_str(), &startup, &process)) {
        MessageBoxW(nullptr, L"Could not start the native game runner. Check that ps2run.exe and SDL2.dll are present.",
                    L"Ape Escape: Pumped & Primed", MB_OK | MB_ICONERROR);
        return 1;
    }
    CloseHandle(process.hThread);
    WaitForSingleObject(process.hProcess, INFINITE);
    DWORD code = 1;
    GetExitCodeProcess(process.hProcess, &code);
    CloseHandle(process.hProcess);
    return static_cast<int>(code);
}
