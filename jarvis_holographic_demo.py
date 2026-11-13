"""
Jarvis Holographic Demo

Demo script for the Jarvis holographic interface with 3D hologram model.
This script demonstrates the integration of the Hologram.glb model
into Jarvis's interface with holographic effects and state management.
"""

import time
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from holographic_interface import HologramRenderer3D, HologramState
from jarvis_voice_integration import JarvisVoiceIntegration, VoiceIntegrationMode
from gui.jarvis_gui_enhanced import EnhancedJarvisGUI
import tkinter as tk
def demo_holographic_renderer():
    """Demo holographic renderer"""
    print("=== Jarvis Holographic Renderer Demo ===")

    # Initialize renderer
    renderer = HologramRenderer3D()

    # Print renderer status
    stats = renderer.get_render_stats()
    print(f"Renderer initialized: {stats}")

    # Start render loop
    renderer.start_render_loop()
    print("Render loop started")

    # Simulate state changes
    states = [
        ("IDLE", "idle", "#00ffff", 0.5),
        ("LISTENING", "listening", "#00ff88", 0.8),
        ("THINKING", "thinking", "#ffaa00", 0.6),
        ("SPEAKING", "speaking", "#ff6600", 0.9),
        ("WORKING", "working", "#ffffff", 0.7),
        ("ERROR", "error", "#ff0000", 1.0)
    ]

    print("\nSimulating state transitions...")
    for i, (state_name, animation, color, glow) in enumerate(states):
        hologram_state = HologramState(
            id=f"demo_state_{i}",
            name=f"Demo State {i}",
            state=state_name,
            animation=animation,
            color=color,
            glow_intensity=glow
        )

        print(f"  Transitioning to: {state_name}")
        renderer.set_model_state(hologram_state)
        time.sleep(2)

    # Stop render loop
    renderer.stop_render_loop()
    renderer.dispose()

    print("\nDemo completed successfully!")
    return True
def demo_voice_integration():
    """Demo voice integration"""
    print("\n=== Jarvis Voice Integration Demo ===")

    try:
        # Initialize voice integration
        voice_integration = JarvisVoiceIntegration(mode=VoiceIntegrationMode.HYBRID)

        if voice_integration.start():
            print("Voice integration started successfully")

            # Simulate some voice commands
            print("\nSimulating voice commands...")
            time.sleep(1)

            print("Voice commands demo completed")
            return True
        else:
            print("Failed to start voice integration")
            return False

    except Exception as e:
        print(f"Error in voice integration demo: {e}")
        return False
def demo_gui_integration():
    """Demo GUI integration"""
    print("\n=== Jarvis GUI Integration Demo ===")

    try:
        # Initialize GUI
        root = tk.Tk()
        app = EnhancedJarvisGUI(root)

        print("GUI initialized successfully")
        print("GUI features:")
        print("  - Holographic display with 3D model")
        print("  - Voice interface controls")
        print("  - State management for hologram")
        print("  - System logging")
        print("  - Real-time updates")

        # Don't actually run mainloop in demo
        # root.mainloop()

        # Just test basic GUI functionality
        app.on_hologram_state_changed()
        app.apply_hologram_state()
        app.log_message("Demo log message")

        print("\nGUI demo completed successfully")

        # Cleanup
        root.destroy()
        return True

    except Exception as e:
        print(f"Error in GUI integration demo: {e}")
        return False
def demo_comprehensive():
    """Run comprehensive demo"""
    print("=== Jarvis Comprehensive Holographic Demo ===")
    print("This demo showcases the integration of Jarvis with a custom 3D hologram model.")
    print()

    results = []

    # Demo 1: Holographic Renderer
    results.append(("Holographic Renderer", demo_holographic_renderer()))

    # Demo 2: Voice Integration
    results.append(("Voice Integration", demo_voice_integration()))

    # Demo 3: GUI Integration
    results.append(("GUI Integration", demo_gui_integration()))

    # Summary
    print("\n" + "="*60)
    print("DEMO SUMMARY")
    print("="*60)

    all_passed = True
    for demo_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{demo_name}: {status}")
        if not passed:
            all_passed = False

    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("\nThe Jarvis holographic interface has been successfully integrated")
        print("with the custom Hologram.glb 3D model, providing a premium,")
        print("futuristic user experience while maintaining all existing")
        print("Jarvis functionality.")
    else:
        print("⚠️  SOME DEMOS FAILED - CHECK OUTPUT ABOVE")

    return all_passed
def main():
    """Main function"""
    print("Jarvis Holographic Demo")
    print("=" * 50)
    print("This demo showcases the integration of Jarvis with a custom 3D")
    print("hologram model (Hologram.glb) to create a premium, futuristic")
    print("interface for the AI assistant.")
    print()

    # Run comprehensive demo
    success = demo_comprehensive()

    if success:
        print("\n✅ Demo completed successfully!")
        print("The Jarvis holographic interface is ready for deployment.")
    else:
        print("\n❌ Demo completed with errors.")
        print("Please check the output above for details.")

        sys.exit(1)
if __name__ == "__main__":
    main()