import { useEffect, useRef, useState } from 'react'
import * as THREE from 'three'
import { HologramState } from '../types'

interface HologramProps {
  state: HologramState
}

export default function Hologram({ state }: HologramProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    let animationFrame: number
    let scene: any
    let camera: any
    let renderer: any
    let character: any
    let particles: any
    let time = 0

    const init = () => {
      if (!containerRef.current) return

      scene = new THREE.Scene()
      scene.fog = new THREE.FogExp2(0x0a0f0d, 0.02)

      camera = new THREE.PerspectiveCamera(45, containerRef.current.clientWidth / containerRef.current.clientHeight, 0.1, 100)
      camera.position.set(0, 1, 3.5)
      camera.lookAt(0, 0, 0)

      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' })
      renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight)
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
      renderer.shadowMap.enabled = true
      renderer.shadowMap.type = THREE.PCFSoftShadowMap
      renderer.toneMapping = THREE.ACESFilmicToneMapping
      renderer.outputColorSpace = THREE.SRGBColorSpace

      containerRef.current.appendChild(renderer.domElement)

      const ambientLight = new THREE.AmbientLight(0xffffff, 0.3)
      scene.add(ambientLight)

      const keyLight = new THREE.PointLight(0x4ade80, 2, 10)
      keyLight.position.set(3, 3, 3)
      scene.add(keyLight)

      const rimLight = new THREE.SpotLight(0xd4a574, 1, 15, 0.5, 0.5, 1)
      rimLight.position.set(-3, 2, 4)
      rimLight.lookAt(0, 0, 0)
      scene.add(rimLight)

      character = new THREE.Group()

      const headGeo = new THREE.SphereGeometry(0.45, 32, 32)
      const headMat = new THREE.MeshStandardMaterial({
        color: 0x4ade80,
        emissive: 0x004d40,
        emissiveIntensity: 1,
        roughness: 0.1,
        metalness: 0.8,
        transparent: true,
        opacity: 0.9,
      })
      const head = new THREE.Mesh(headGeo, headMat)
      head.castShadow = true
      head.position.y = 0.5
      character.add(head)

      const torsoGeo = new THREE.CylinderGeometry(0.35, 0.35, 0.9, 32)
      const torsoMat = new THREE.MeshStandardMaterial({
        color: 0x4ade80,
        emissive: 0x003d2e,
        emissiveIntensity: 0.8,
        roughness: 0.15,
        metalness: 0.7,
        transparent: true,
        opacity: 0.85,
      })
      const torso = new THREE.Mesh(torsoGeo, torsoMat)
      torso.castShadow = true
      torso.position.y = -0.2
      character.add(torso)

      const shoulderGeo = new THREE.SphereGeometry(0.25, 16, 16)
      const shoulderMat = new THREE.MeshStandardMaterial({
        color: 0x4ade80,
        emissive: 0x003d2e,
        emissiveIntensity: 0.6,
        transparent: true,
        opacity: 0.8,
      })

      const lShoulder = new THREE.Mesh(shoulderGeo, shoulderMat)
      lShoulder.position.set(-0.5, 0.25, 0)
      character.add(lShoulder)

      const rShoulder = new THREE.Mesh(shoulderGeo, shoulderMat)
      rShoulder.position.set(0.5, 0.25, 0)
      character.add(rShoulder)

      const armGeo = new THREE.CylinderGeometry(0.12, 0.12, 0.7, 16)
      const lArm = new THREE.Mesh(armGeo, shoulderMat)
      lArm.position.set(-0.75, -0.15, 0)
      lArm.rotation.z = Math.PI / 6
      character.add(lArm)

      const rArm = new THREE.Mesh(armGeo, shoulderMat)
      rArm.position.set(0.75, -0.15, 0)
      rArm.rotation.z = -Math.PI / 6
      character.add(rArm)

      const handGeo = new THREE.SphereGeometry(0.1, 12, 12)
      const lHand = new THREE.Mesh(handGeo, shoulderMat)
      lHand.position.set(-1.25, -0.65, 0)
      character.add(lHand)

      const rHand = new THREE.Mesh(handGeo, shoulderMat)
      rHand.position.set(1.25, -0.65, 0)
      character.add(rHand)

      character.position.set(0, 0, 0)
      scene.add(character)

      const gridHelper = new THREE.GridHelper(10, 20, 0x4ade80, 0x000000)
      gridHelper.position.y = -1.2
      gridHelper.material.opacity = 0.15
      gridHelper.material.transparent = true
      scene.add(gridHelper)

      const ringGeo = new THREE.RingGeometry(0.5, 0.6, 32)
      const ringMat = new THREE.MeshBasicMaterial({
        color: 0x4ade80,
        transparent: true,
        opacity: 0.3,
        side: THREE.DoubleSide,
      })
      const ring = new THREE.Mesh(ringGeo, ringMat)
      ring.rotation.x = Math.PI / 2
      ring.position.y = -1.15
      scene.add(ring)

      const particleCount = 150
      const particlesGeo = new THREE.BufferGeometry()
      const positions = new Float32Array(particleCount * 3)
      const velocities = new Float32Array(particleCount * 3)

      for (let i = 0; i < particleCount; i++) {
        positions[i * 3] = (Math.random() - 0.5) * 4
        positions[i * 3 + 1] = (Math.random() - 0.5) * 4
        positions[i * 3 + 2] = (Math.random() - 0.5) * 4
        velocities[i * 3] = (Math.random() - 0.5) * 0.02
        velocities[i * 3 + 1] = (Math.random() - 0.5) * 0.02
        velocities[i * 3 + 2] = (Math.random() - 0.5) * 0.02
      }

      particlesGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3))
      const particlesMat = new THREE.PointsMaterial({
        color: 0x4ade80,
        size: 0.02,
        transparent: true,
        opacity: 0.6,
      })
      particles = new THREE.Points(particlesGeo, particlesMat)
      scene.add(particles)

      const glowGeo = new THREE.SphereGeometry(1.5, 32, 32)
      const glowMat = new THREE.MeshBasicMaterial({
        color: 0x4ade80,
        transparent: true,
        opacity: 0.05,
        side: THREE.BackSide,
      })
      const glow = new THREE.Mesh(glowGeo, glowMat)
      scene.add(glow)

      const handleResize = () => {
        if (!containerRef.current) return
        camera.aspect = containerRef.current.clientWidth / containerRef.current.clientHeight
        camera.updateProjectionMatrix()
        renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight)
      }

      window.addEventListener('resize', handleResize)

      const animate = () => {
        animationFrame = requestAnimationFrame(animate)
        time += 0.01

        const breath = Math.sin(time * 1.5) * 0.02
        character.scale.setScalar(1 + breath)
        character.position.y = Math.sin(time * 2) * 0.02

        if (head) {
          head.rotation.y = Math.sin(time * 0.5) * 0.1
          head.rotation.x = Math.cos(time * 0.7) * 0.05
        }

        if (lArm && rArm) {
          const armSway = Math.sin(time * 2) * 0.15
          lArm.rotation.z = Math.PI / 6 + armSway
          rArm.rotation.z = -Math.PI / 6 - armSway
        }

        if (ring) {
          ring.rotation.y += 0.02
          ring.rotation.z += 0.01
        }

        const stateColors: Record<string, number> = {
          IDLE: 0x4ade80,
          LISTENING: 0x22d3ee,
          THINKING: 0xfbbf24,
          SPEAKING: 0xa78bfa,
          WORKING: 0xef4444,
          ERROR: 0xf43f5e,
        }

        const targetColor = stateColors[state] || 0x4ade80
        const lerpSpeed = 0.05

        headMat.color.lerpColors(headMat.color, new THREE.Color(targetColor), lerpSpeed)
        headMat.emissive.lerpColors(headMat.emissive, new THREE.Color(targetColor).multiplyScalar(0.3), lerpSpeed)
        torsoMat.color.lerpColors(torsoMat.color, new THREE.Color(targetColor), lerpSpeed)
        torsoMat.emissive.lerpColors(torsoMat.emissive, new THREE.Color(targetColor).multiplyScalar(0.3), lerpSpeed)
        ringMat.color.lerpColors(ringMat.color, new THREE.Color(targetColor), lerpSpeed)
        keyLight.color.lerpColors(keyLight.color, new THREE.Color(targetColor), lerpSpeed)
        particlesMat.color.lerpColors(particlesMat.color, new THREE.Color(targetColor), lerpSpeed)

        const positions = particlesGeo.attributes.position.array as Float32Array
        for (let i = 0; i < particleCount; i++) {
          positions[i * 3] += velocities[i * 3]
          positions[i * 3 + 1] += velocities[i * 3 + 1]
          positions[i * 3 + 2] += velocities[i * 3 + 2]
          if (Math.abs(positions[i * 3]) > 2) velocities[i * 3] *= -1
          if (Math.abs(positions[i * 3 + 1]) > 2) velocities[i * 3 + 1] *= -1
          if (Math.abs(positions[i * 3 + 2]) > 2) velocities[i * 3 + 2] *= -1
        }
        particlesGeo.attributes.position.needsUpdate = true

        const pulseIntensity = state === 'LISTENING' || state === 'THINKING' || state === 'WORKING' ? 1 : 0.5
        glowMat.opacity = 0.05 + Math.sin(time * 2 * pulseIntensity) * 0.03 * pulseIntensity

        renderer.render(scene, camera)
      }

      animate()
      setIsReady(true)

      return () => {
        cancelAnimationFrame(animationFrame)
        window.removeEventListener('resize', handleResize)
        if (renderer) renderer.dispose()
        containerRef.current?.removeChild(renderer.domElement)
      }
    }

    return init()
  }, [state])

  return (
    <div
      ref={containerRef}
      className="absolute inset-0 w-full h-full"
    />
  )
}
