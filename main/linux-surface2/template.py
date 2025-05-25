# Template for linux-surface2, based on linux-stable
pkgname = "linux-surface2"
_base_kernel_ver = "6.14.5"  # CHOOSE YOUR TARGET BASE KERNEL VERSION
pkgver = _base_kernel_ver
pkgrel = 0  # Start at 0 for a new package version

archs = ["x86_64"]
build_style = "linux-kernel"
# FLAVOR=surface2 assumes main/linux-surface2/files/surface2.config or surface2-x86_64.config exists
# Patches from main/linux-surface2/patches/ for _base_kernel_ver should be applied by the build style.
configure_args = ["FLAVOR=surface2", f"RELEASE={pkgrel}"]
make_dir = "build"
make_install_env = {"ZSTD_CLEVEL": "9"} # From linux-stable

hostmakedepends = ["base-kernel-devel"]
depends = ["base-kernel"]
provides = ["linux"] # Provides a generic "linux"

pkgdesc = "Linux kernel with linux-surface patches"
subdesc = f"based on v{_base_kernel_ver}"
license = "GPL-2.0-only"
url = "https://github.com/linux-surface/linux-surface" # Patchset URL
# Source the vanilla kernel tarball
source = f"https://cdn.kernel.org/pub/linux/kernel/v{_base_kernel_ver[0]}.x/linux-{_base_kernel_ver}.tar.xz#/{pkgname}-base-{_base_kernel_ver}.tar.xz"
sha256 = "SKIP" # MUST be updated after first fetch using prepare-upgrade

# Options from linux-stable, adjust if necessary
options = [
    "!check",
    "!debug",
    "!strip",
    "!scanrundeps",
    "!scanshlibs",
    "!lto",
    "textrels",
    "execstack",
    "foreignelf",  # vdso32
]

# Copied from linux-stable, for `cbuild ... custom:generate-configs`
if self.current_target == "custom:generate-configs":
    hostmakedepends += ["base-cross", "ncurses-devel"]

# Copied from linux-stable
if self.profile().cross:
    broken = "linux-devel does not come out right" # Standard kernel packages often have issues with cross-compiled -devel

# Precautionary empty pre_configure to avoid potential upstream script issues
def pre_configure(self):
    self.log(f"Skipping default pre_configure for {self.pkgname} to avoid potential stdout_to_file error.")
    # Add ls command for diagnostics if needed again:
    # self.log(f"Listing contents of {self.chroot_cwd} before configure phase:")
    # self.do("ls", "-alph", self.chroot_cwd)
    pass

# The linux-kernel build style is expected to handle prepare, build, and install.
# Patches should be placed in main/linux-surface2/patches/
# Kernel config should be in main/linux-surface2/files/surface2.config (or surface2-x86_64.config)

@subpackage(f"{pkgname}-devel")
def _(self):
    self.pkgdesc = pkgdesc # Inherits main pkgdesc
    self.subdesc = f"development files (for v{_base_kernel_ver} base)"
    self.depends += ["clang", "pahole"] # From linux-stable-devel, plus pahole
    self.options = ["foreignelf", "execstack", "!scanshlibs"]
    # Standard paths for -devel package, build style should handle population
    return ["usr/src", "usr/lib/modules/*/build"]

@subpackage(f"{pkgname}-dbg", self.build_dbg)
def _(self):
    self.pkgdesc = pkgdesc # Inherits main pkgdesc
    self.subdesc = f"debug symbols (for v{_base_kernel_ver} base)"
    self.options = [ # From linux-stable-dbg
        "!scanrundeps",
        "!strip",
        "!scanshlibs",
        "foreignelf",
        "execstack",
        "textrels",
    ]
    # Standard paths for -dbg package
    return ["usr/lib/debug", "usr/lib/modules/*/apk-dist/boot/System.map-*"]