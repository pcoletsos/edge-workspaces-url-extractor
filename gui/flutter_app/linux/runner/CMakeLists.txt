cmake_minimum_required(VERSION 3.13)
project(runner LANGUAGES CXX)

# Define the application target. To change its name, change BINARY_NAME in the
# top-level CMakeLists.txt, not the value here, or `flutter run` will no longer
# work.
#
# Any new source files that you add to the application should be added here.
add_executable(${BINARY_NAME}
  "main.cc"
  "my_application.cc"
  "${FLUTTER_MANAGED_DIR}/generated_plugin_registrant.cc"
)

# Apply the standard set of build settings. This can be removed for applications
# that need different build settings.
apply_standard_settings(${BINARY_NAME})

# Add preprocessor definitions for the application ID.
add_definitions(-DAPPLICATION_ID="${APPLICATION_ID}")

# Add dependency libraries. Add any application-specific dependencies here.
target_link_libraries(${BINARY_NAME} PRIVATE flutter)
target_link_libraries(${BINARY_NAME} PRIVATE PkgConfig::GTK)

target_include_directories(${BINARY_NAME} PRIVATE "${CMAKE_SOURCE_DIR}")

set(REPO_ROOT "${CMAKE_SOURCE_DIR}/../../..")
set(GUI_BACKEND_SOURCE "${REPO_ROOT}/dist/edge-workspace-links-gui-backend")
set(GUI_BACKEND_TARGET "${PROJECT_BINARY_DIR}/edge-workspace-links-gui-backend")
set(GUI_BACKEND_TARGET "${GUI_BACKEND_TARGET}" PARENT_SCOPE)

# Copy the prebuilt GUI backend into the bundle root so the desktop runner can
# resolve a sibling executable at runtime without a Python source checkout.
# The top-level install(PROGRAMS ...) step preserves executable permissions in
# the final bundle, so this build-tree copy only needs the file contents.
add_custom_command(
  TARGET ${BINARY_NAME}
  POST_BUILD
  COMMAND ${CMAKE_COMMAND} -E copy_if_different "${GUI_BACKEND_SOURCE}" "${GUI_BACKEND_TARGET}"
  WORKING_DIRECTORY "${REPO_ROOT}"
  VERBATIM
)
