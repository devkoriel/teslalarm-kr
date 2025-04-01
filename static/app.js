// File: static/app.js

// Destructure Chakra UI components from the UMD bundle
const { ChakraProvider, Box, Button, HStack, Text } =
    window["@chakra-ui/react"];

const App = () => {
    return (
        <ChakraProvider>
            <Box textAlign="center" color="white" p={10}>
                <Text fontSize="2xl" mb={6}>
                    테스알림 Korea 🇰🇷 텔레그램 채널에 오신 것을 환영합니다!
                </Text>
                <HStack spacing={8} justify="center">
                    <Button
                        colorScheme="blue"
                        size="lg"
                        borderRadius="full"
                        onClick={() =>
                            window.open("https://t.me/tesalarmKR", "_blank")
                        }
                    >
                        채널 바로가기
                    </Button>
                    <Button
                        colorScheme="green"
                        size="lg"
                        borderRadius="full"
                        onClick={() =>
                            window.open("https://donate.example.com", "_blank")
                        }
                    >
                        기부하기
                    </Button>
                </HStack>
            </Box>
        </ChakraProvider>
    );
};

ReactDOM.createRoot(document.getElementById("root")).render(<App />);

// Three.js animation for the background
let scene, camera, renderer, group;
function initAnimation() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(
        75,
        window.innerWidth / window.innerHeight,
        0.1,
        1000
    );
    renderer = new THREE.WebGLRenderer({
        canvas: document.getElementById("animation-canvas"),
        alpha: true,
    });
    renderer.setSize(window.innerWidth, window.innerHeight);

    // Create a group of boxes representing Tesla models drifting in space
    group = new THREE.Group();
    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const material = new THREE.MeshBasicMaterial({ color: 0xffffff });
    for (let i = 0; i < 20; i++) {
        const box = new THREE.Mesh(geometry, material);
        box.position.set(
            (Math.random() - 0.5) * 50,
            (Math.random() - 0.5) * 50,
            (Math.random() - 0.5) * 50
        );
        group.add(box);
    }
    scene.add(group);
    camera.position.z = 30;

    // Update renderer and camera on window resize
    window.addEventListener("resize", () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });

    // Animation loop: rotate the group continuously
    function animate() {
        requestAnimationFrame(animate);
        group.rotation.x += 0.001;
        group.rotation.y += 0.001;
        renderer.render(scene, camera);
    }
    animate();
}

initAnimation();
