// build.rs
// This script runs during the build process to configure the build environment.

fn main() {
    // Tell Cargo to re-run this script if build.rs changes
    println!("cargo:rerun-if-changed=build.rs");
    
    // Set up WASM-specific optimizations when targeting wasm32
    if std::env::var("TARGET").unwrap_or_default().contains("wasm32") {
        // Tell the compiler to optimize for size
        println!("cargo:rustc-flag=-Copt-level=s");
        
        // Enable link-time optimization
        println!("cargo:rustc-flag=-Clto=yes");
        
        // Reduce code bloat
        println!("cargo:rustc-flag=-Ccodegen-units=1");
        
        // Disable debug info to reduce size
        println!("cargo:rustc-flag=-Cdebuginfo=0");
    }
}
