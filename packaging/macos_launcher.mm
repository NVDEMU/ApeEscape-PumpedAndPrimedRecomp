#import <AppKit/AppKit.h>

#include <cerrno>
#include <cstdlib>
#include <filesystem>
#include <spawn.h>
#include <string>
#include <sys/wait.h>
#include <unistd.h>
#include <vector>

extern char **environ;

int main(int argc, char **argv) {
    @autoreleasepool {
        [NSApplication sharedApplication];
        [NSApp setActivationPolicy:NSApplicationActivationPolicyRegular];
        [NSApp activateIgnoringOtherApps:YES];
        NSOpenPanel *panel = [NSOpenPanel openPanel];
        panel.canChooseFiles = YES;
        panel.canChooseDirectories = NO;
        panel.allowsMultipleSelection = NO;
        panel.canCreateDirectories = NO;
        panel.title = @"Choose your Pumped & Primed disc image";
        panel.message = @"Select an ISO image made from your own PlayStation 2 disc dump.";
        panel.prompt = @"Play";
        panel.allowedFileTypes = @[@"iso"];
        if ([panel runModal] != NSModalResponseOK || panel.URL == nil) return 0;

        const char *isoUtf8 = panel.URL.path.UTF8String;
        if (!isoUtf8 || argc < 1 || !argv[0]) return 2;
        const std::filesystem::path iso = std::filesystem::absolute(isoUtf8);
        const std::filesystem::path self = std::filesystem::absolute(argv[0]);
        const std::filesystem::path gameDir = self.parent_path().parent_path() / "Resources" / "Game";
        const std::filesystem::path runner = gameDir / "ps2run";
        const std::filesystem::path elf = gameDir / "SLUS_210.96";

        const char *home = std::getenv("HOME");
        if (!home) return 2;
        const std::filesystem::path saves =
            std::filesystem::path(home) / "Library" / "Application Support" / "Ape Escape Pumped and Primed Recomp";
        std::filesystem::create_directories(saves);
        const std::filesystem::path card = saves / "memorycard.ps2";

        std::vector<std::string> args = {
            runner.string(), elf.string(), "--disc", iso.string(), "--window", "--memcard", card.string()
        };
        std::vector<char *> raw;
        raw.reserve(args.size() + 1);
        for (auto &arg : args) raw.push_back(arg.data());
        raw.push_back(nullptr);

        pid_t child = 0;
        const int spawnResult = posix_spawn(&child, runner.c_str(), nullptr, nullptr, raw.data(), environ);
        if (spawnResult != 0) {
            NSString *message = [NSString stringWithFormat:@"Could not start the native game runner (error %d).", spawnResult];
            NSAlert *alert = [[NSAlert alloc] init];
            alert.messageText = @"Ape Escape: Pumped & Primed Recompiled";
            alert.informativeText = message;
            [alert runModal];
            return 1;
        }
        int status = 0;
        while (waitpid(child, &status, 0) < 0) {
            if (errno == EINTR) continue;
            return 1;
        }
        if (WIFEXITED(status)) return WEXITSTATUS(status);
        return 1;
    }
}
