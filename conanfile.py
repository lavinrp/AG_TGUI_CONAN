import os, shutil
from conans import ConanFile, CMake, tools

class PackagerTGUI(ConanFile):
    name = 'tgui'
    version = '0.8'
    branch = 'stable'
    settings = 'os', 'compiler', 'arch', 'build_type'
    options = {'shared': [True, False], 'cpp17': [True, False]}
    default_options = 'shared=True', 'cpp17=True'
    generators = 'cmake'
    license = 'zlib/png'
    url='https://github.com/texus/TGUI'
    exports = ['CMakeLists.txt']
    requires = "sfml/2.5.0@bincrafters/stable"
    so_version = '0.8'

    def source(self):
        self.run("git clone https://github.com/texus/TGUI.git")
        self.run("cd TGUI && git checkout 0.8")
        # its in source/tgui/CMakeLists.txt
        tools.replace_in_file()

    def build(self):
        cmake = CMake(self.settings)
        self.run('mkdir _build')
        self.run('cd _build && cmake ../%s -DBUILD_SHARED_LIBS=%s -DCMAKE_INSTALL_PREFIX=../install %s' %
            ("TGUI", 'ON' if self.options.shared else 'OFF', cmake.command_line)
        )
        if self.settings.os == 'Windows':
            self.run('cd _build && cmake --build . %s --target install --config %s' % (cmake.build_config, self.settings.build_type))
        else:
            self.run('cd _build && cmake --build . %s -- -j2 install' % cmake.build_config)

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["TGUI_SHARED_LIBS"] = self.options.shared
        if self.options.cpp17:
            cmake.definitions["TGUI_USE_CPP17"] = True

    def add_libraries_from_pc(self, library, static=None):
        if static is None:
            static = not self.options.shared
        pkg_config = tools.PkgConfig(library, static=static)
        libs = [lib[2:] for lib in pkg_config.libs_only_l]  # cut -l prefix
        lib_paths = [lib[2:] for lib in pkg_config.libs_only_L]  # cut -L prefix
        self.cpp_info.libs.extend(libs)
        self.cpp_info.libdirs.extend(lib_paths)
        self.cpp_info.sharedlinkflags.extend(pkg_config.libs_only_other)
        self.cpp_info.exelinkflags.extend(pkg_config.libs_only_other)

    def package(self):
        self.copy('*.*', 'include', 'install/include', keep_path=True)
        self.copy(pattern='*.a', dst='lib', src='install/lib', keep_path=False)
        self.copy(pattern='*.so.' + self.so_version, dst='lib', src='install/lib', keep_path=False)
        self.copy(pattern='*.lib', dst='lib', src='install/lib', keep_path=False)
        self.copy(pattern='*.dll', dst='bin', src='install/lib', keep_path=False)

    def package_info(self):
        if (not self.settings.os == 'Windows') and self.options.shared:
            self.cpp_info.libs = [':libtgui'
                                  + ('-d' if self.settings.build_type == 'Debug' else '')
                                  + '.so.'
                                  + self.so_version]
        else:
            self.cpp_info.libs = ['tgui'
                                  + ('' if self.options.shared else '-s')
                                  + ('-d' if self.settings.build_type == 'Debug' else '')]

