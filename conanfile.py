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

    _source_subfolder = 'source_subfolder'
    _build_subfolder = 'build_subfolder'

    def source(self):
        self.run("git clone https://github.com/texus/TGUI.git")
        self.run("cd TGUI && git checkout 0.8 && cd ..")
        # its in source/tgui/CMakeLists.txt
        print(os.getcwd())
        os.listdir(os.getcwd())
        tools.replace_in_file("./TGUI/src/TGUI/CMakeLists.txt",
         "if(DEFINED SFML_LIBRARIES)\n    # SFML found via FindSFML.cmake\n    target_include_directories(tgui PRIVATE ${SFML_INCLUDE_DIR})\n    target_link_libraries(tgui PRIVATE ${SFML_LIBRARIES} ${SFML_DEPENDENCIES})\nelse()\n    # SFML found via SFMLConfig.cmake\n    target_link_libraries(tgui PRIVATE sfml-graphics)\nendif()",
         "include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)\nconan_basic_setup()\ntarget_link_libraries(tgui ${CONAN_LIBS})")

    def build(self):
        if self.settings.compiler == 'Visual Studio':
            with tools.vcvars(self.settings, force=True, filter_known_paths=False):
                cmake = self.configure_cmake()
        else:
            cmake = self.configure_cmake()
        cmake.build()

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["TGUI_SHARED_LIBS"] = self.options.shared
        if self.options.cpp17:
            cmake.definitions["TGUI_USE_CPP17"] = True

        #os.rename(self._source_subfolder + '/extlibs', self._source_subfolder + '/ext')
        #cmake.configure(build_folder=self._build_subfolder)
        #os.rename(self._source_subfolder + '/ext', self._source_subfolder + '/extlibs')
        cmake.configure()
        return cmake

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
        # self.copy(pattern='License.md', dst='licenses', src=self._source_subfolder)
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

