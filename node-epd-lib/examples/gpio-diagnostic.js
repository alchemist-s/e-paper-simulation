#!/usr/bin/env node

const fs = require("fs").promises;
const { exec } = require("child_process");
const { promisify } = require("util");

const execAsync = promisify(exec);

async function gpioDiagnostic() {
  console.log("GPIO Diagnostic Test");
  console.log("===================");

  try {
    // Check 1: GPIO directory exists
    console.log("\n1. Checking GPIO directory...");
    try {
      await fs.access("/sys/class/gpio");
      console.log("✅ /sys/class/gpio directory exists");
    } catch (err) {
      console.log("❌ /sys/class/gpio directory not accessible");
      return;
    }

    // Check 2: GPIO export file permissions
    console.log("\n2. Checking GPIO export permissions...");
    try {
      const exportStats = await fs.stat("/sys/class/gpio/export");
      console.log(
        `✅ GPIO export file exists (mode: ${exportStats.mode.toString(8)})`
      );
    } catch (err) {
      console.log("❌ Cannot access GPIO export file:", err.message);
    }

    // Check 3: Current user and groups
    console.log("\n3. Checking user permissions...");
    try {
      const { stdout: whoami } = await execAsync("whoami");
      const { stdout: groups } = await execAsync("groups");
      console.log(`Current user: ${whoami.trim()}`);
      console.log(`User groups: ${groups.trim()}`);

      if (groups.includes("gpio")) {
        console.log("✅ User is in gpio group");
      } else {
        console.log("⚠️  User is NOT in gpio group");
      }

      if (groups.includes("spi")) {
        console.log("✅ User is in spi group");
      } else {
        console.log("⚠️  User is NOT in spi group");
      }
    } catch (err) {
      console.log("❌ Cannot check user permissions:", err.message);
    }

    // Check 4: Test GPIO export as current user
    console.log("\n4. Testing GPIO export...");

    // First, check what GPIO pins are already exported
    try {
      const { stdout: existingGpios } = await execAsync(
        'ls /sys/class/gpio/ | grep gpio || echo "No GPIO pins exported"'
      );
      console.log(`Currently exported GPIO pins: ${existingGpios.trim()}`);
    } catch (err) {
      console.log("Cannot check existing GPIO pins:", err.message);
    }

    // Check GPIO chip information
    console.log("\n4a. Checking GPIO chip information...");
    try {
      const { stdout: chipInfo } = await execAsync(
        'cat /sys/class/gpio/gpiochip*/label 2>/dev/null || echo "No labels found"'
      );
      console.log(`GPIO chip labels: ${chipInfo.trim()}`);

      const { stdout: chipBase } = await execAsync(
        'cat /sys/class/gpio/gpiochip*/base 2>/dev/null || echo "No base found"'
      );
      console.log(`GPIO chip base numbers: ${chipBase.trim()}`);
    } catch (err) {
      console.log("Cannot check GPIO chip info:", err.message);
    }

    // Try GPIO 512 (first chip base) instead of 17
    try {
      await fs.writeFile("/sys/class/gpio/export", "512");
      console.log("✅ Successfully exported GPIO 512");

      // Check if the directory was created
      try {
        await fs.access("/sys/class/gpio/gpio512");
        console.log("✅ GPIO 512 directory created");

        // Try to set direction
        await fs.writeFile("/sys/class/gpio/gpio512/direction", "out");
        console.log("✅ Successfully set GPIO 512 to output");

        // Try to write a value
        await fs.writeFile("/sys/class/gpio/gpio512/value", "1");
        console.log("✅ Successfully wrote to GPIO 512");

        // Clean up
        await fs.writeFile("/sys/class/gpio/unexport", "512");
        console.log("✅ Successfully unexported GPIO 512");
      } catch (err) {
        console.log("❌ GPIO 512 directory not accessible:", err.message);
      }
    } catch (err) {
      console.log("❌ Cannot export GPIO 512:", err.message);
      console.log("   This might be a permission issue");
    }

    // Check 5: SPI devices
    console.log("\n5. Checking SPI devices...");
    try {
      const { stdout: spidev } = await execAsync(
        'ls /dev/spidev* 2>/dev/null || echo "No SPI devices found"'
      );
      console.log(`SPI devices: ${spidev.trim()}`);

      if (spidev.includes("spidev0.0")) {
        console.log("✅ SPI device spidev0.0 found");
      } else {
        console.log("⚠️  SPI device not found - SPI might not be enabled");
      }
    } catch (err) {
      console.log("❌ Cannot check SPI devices:", err.message);
    }

    // Check 6: System information
    console.log("\n6. System information...");
    try {
      const { stdout: arch } = await execAsync("uname -m");
      const { stdout: os } = await execAsync(
        "cat /etc/os-release | grep PRETTY_NAME"
      );
      console.log(`Architecture: ${arch.trim()}`);
      console.log(`OS: ${os.trim()}`);
    } catch (err) {
      console.log("❌ Cannot get system info:", err.message);
    }

    console.log("\n📋 Summary:");
    console.log("If you see ❌ errors above, you may need to:");
    console.log("1. Add user to gpio group: sudo usermod -a -G gpio $USER");
    console.log("2. Add user to spi group: sudo usermod -a -G spi $USER");
    console.log("3. Enable SPI: sudo raspi-config");
    console.log("4. Reboot: sudo reboot");
  } catch (error) {
    console.error("Diagnostic failed:", error);
  }
}

// Run the diagnostic
gpioDiagnostic().catch(console.error);
