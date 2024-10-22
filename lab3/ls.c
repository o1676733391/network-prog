#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <dirent.h>
#include <sys/stat.h>
#include <time.h>
#include <grp.h>
#include <pwd.h>

#define MAX_PATH_LENGTH 1024

// Function to print file permissions in a human-readable format
void print_permissions(mode_t mode) {
    printf((mode & S_IFDIR) ? "d" : "-");
    printf((mode & S_IRUSR) ? "r" : "-");
    printf((mode & S_IWUSR) ? "w" : "-");
    printf((mode & S_IXUSR) ? "x" : "-");
    printf((mode & S_IRGRP) ? "r" : "-");
    printf((mode & S_IWGRP) ? "w" : "-");
    printf((mode & S_IXGRP) ? "x" : "-");
    printf((mode & S_IROTH) ? "r" : "-");
    printf((mode & S_IWOTH) ? "w" : "-");
    printf((mode & S_IXOTH) ? "x" : "-");
}

// Function to get the file size in human-readable format
char *get_file_size(off_t size) {
    static char size_str[10];
    if (size < 1024) {
        sprintf(size_str, "%lld", size);
    } else if (size < 1048576) {
        sprintf(size_str, "%lldK", size / 1024);
    } else if (size < 1073741824) {
        sprintf(size_str, "%lldM", size / 1048576);
    } else {
        sprintf(size_str, "%lldG", size / 1073741824);
    }
    return size_str;
}

// Function to get the file owner's name
char *get_file_owner(uid_t uid) {
    struct passwd *pw = getpwuid(uid);
    return pw ? pw->pw_name : "unknown";
}

// Function to get the file group's name
char *get_file_group(gid_t gid) {
    struct group *gr = getgrgid(gid);
    return gr ? gr->gr_name : "unknown";
}

// Function to get the file's last modified time in human-readable format
char *get_file_mtime(time_t mtime) {
    static char time_str[20];
    struct tm *tm = localtime(&mtime);
    strftime(time_str, sizeof(time_str), "%b %d %H:%M", tm);
    return time_str;
}

// Function to print file information
void print_file_info(const char *filename, struct stat *file_stat) {
    print_permissions(file_stat->st_mode);
    printf("  ");
    printf("%d ", file_stat->st_nlink);
    printf("%s ", get_file_owner(file_stat->st_uid));
    printf("%s ", get_file_group(file_stat->st_gid));
    printf("%s ", get_file_size(file_stat->st_size));
    printf("%s ", get_file_mtime(file_stat->st_mtime));
    printf("%s\n", filename);
}

// Function to list files in a directory
void list_files(const char *dir_path) {
    DIR *dir;
    struct dirent *entry;
    struct stat file_stat;

    dir = opendir(dir_path);
    if (dir == NULL) {
        perror("opendir");
        return;
    }

    while ((entry = readdir(dir)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }

        char filepath[MAX_PATH_LENGTH];
        snprintf(filepath, MAX_PATH_LENGTH, "%s/%s", dir_path, entry->d_name);

        if (lstat(filepath, &file_stat) == -1) {
            perror("lstat");
            continue;
        }

        print_file_info(entry->d_name, &file_stat);
    }

    closedir(dir);
}

// Main function
int main(int argc, char *argv[]) {
    if (argc == 1) {
        list_files(".");
    } else {
        for (int i = 1; i < argc; i++) {
            list_files(argv[i]);
        }
    }
    return 0;
}