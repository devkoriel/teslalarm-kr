// 언어 설정
let currentLanguage =
    localStorage.getItem("language") ||
    (navigator.language.startsWith("ko") ? "ko" : "en");

// 번역 데이터
const translations = {
    ko: {
        header: {
            features: "기능",
            donate: "후원하기",
        },
        hero: {
            title: "테슬라 뉴스와 정보를 실시간으로",
            description:
                "테슬라 관련 최신 뉴스, 가격 변동, 보조금 정보까지 AI가 분석하여 신뢰도 높은 정보만 제공합니다.",
            joinButton: "텔레그램 채널 참여하기",
            learnMoreButton: "자세히 알아보기",
        },
        features: {
            title: "주요 기능",
            realTimeTitle: "실시간 소식",
            realTimeDesc:
                "테슬라 관련 뉴스를 국내외 신뢰할 수 있는 매체에서 수집하여 제공합니다.",
            aiAnalysisTitle: "AI 신뢰도 분석",
            aiAnalysisDesc:
                "최첨단 AI 기술로 수집된 정보의 신뢰도를 분석하고 검증된 정보만 제공합니다.",
            subsidyInfoTitle: "보조금 정보",
            subsidyInfoDesc:
                "지역별 전기차 보조금 정보를 실시간으로 업데이트하여 알려드립니다.",
            communityTitle: "커뮤니티 정보",
            communityDesc:
                "유용한 테슬라 사용자 팁과 정보를 품질 검증 후 제공합니다.",
        },
        donation: {
            title: "프로젝트 후원하기",
            description:
                "테슬라 알람 KR은 여러분의 후원으로 더 나은 서비스를 제공할 수 있습니다. 카카오페이로 간편하게 후원해 주세요.",
            button: "카카오페이로 후원하기",
            modalTitle: "카카오페이로 후원하기",
            modalDescription:
                "QR 코드를 스캔하여 카카오페이로 후원해 주세요. 소중한 후원에 감사드립니다.",
        },
        footer: {
            copyright: "© 2024 테슬라 알람 KR. All rights reserved.",
            contact: "문의사항",
        },
    },
    en: {
        header: {
            features: "Features",
            donate: "Donate",
        },
        hero: {
            title: "Tesla News & Info in Real-time",
            description:
                "Get the latest Tesla news, price changes, and subsidy information analyzed by AI to provide only reliable information.",
            joinButton: "Join Telegram Channel",
            learnMoreButton: "Learn More",
        },
        features: {
            title: "Key Features",
            realTimeTitle: "Real-time Updates",
            realTimeDesc:
                "Collect Tesla news from reliable domestic and international sources.",
            aiAnalysisTitle: "AI Reliability Analysis",
            aiAnalysisDesc:
                "Cutting-edge AI technology analyzes the reliability of information and provides only verified content.",
            subsidyInfoTitle: "Subsidy Information",
            subsidyInfoDesc:
                "Real-time updates on electric vehicle subsidies by region.",
            communityTitle: "Community Info",
            communityDesc:
                "Useful Tesla user tips and information provided after quality verification.",
        },
        donation: {
            title: "Support the Project",
            description:
                "Tesla Alarm KR can provide better services with your support. Please donate easily with KakaoPay.",
            button: "Donate with KakaoPay",
            modalTitle: "Donate with KakaoPay",
            modalDescription:
                "Scan the QR code to donate via KakaoPay. Thank you for your valuable support.",
        },
        footer: {
            copyright: "© 2024 Tesla Alarm KR. All rights reserved.",
            contact: "Contact Us",
        },
    },
};

// 요소 선택자
const select = (selector) => document.querySelector(selector);
const selectAll = (selector) => document.querySelectorAll(selector);

// 텍스트 설정 함수
function setTranslatedText(selector, key) {
    const element = select(selector);
    if (element) {
        const keys = key.split(".");
        let value = translations[currentLanguage];
        for (let k of keys) {
            if (value && value[k] !== undefined) {
                value = value[k];
            } else {
                console.warn(`Translation key not found: ${key}`);
                return;
            }
        }
        element.textContent = value;
    }
}

// 페이지 번역 함수
function translatePage() {
    // 헤더
    setTranslatedText(".nav-features", "header.features");
    setTranslatedText(".nav-donate", "header.donate");

    // 히어로 섹션
    setTranslatedText(".hero-title", "hero.title");
    setTranslatedText(".hero-description", "hero.description");
    setTranslatedText(".hero-join-button", "hero.joinButton");
    setTranslatedText(".hero-learn-button", "hero.learnMoreButton");

    // 기능 섹션
    setTranslatedText(".features-title", "features.title");
    setTranslatedText(
        ".feature-realtime .feature-title",
        "features.realTimeTitle"
    );
    setTranslatedText(
        ".feature-realtime .feature-description",
        "features.realTimeDesc"
    );
    setTranslatedText(".feature-ai .feature-title", "features.aiAnalysisTitle");
    setTranslatedText(
        ".feature-ai .feature-description",
        "features.aiAnalysisDesc"
    );
    setTranslatedText(
        ".feature-subsidy .feature-title",
        "features.subsidyInfoTitle"
    );
    setTranslatedText(
        ".feature-subsidy .feature-description",
        "features.subsidyInfoDesc"
    );
    setTranslatedText(
        ".feature-community .feature-title",
        "features.communityTitle"
    );
    setTranslatedText(
        ".feature-community .feature-description",
        "features.communityDesc"
    );

    // 후원 섹션
    setTranslatedText(".donation-title", "donation.title");
    setTranslatedText(".donation-description", "donation.description");
    setTranslatedText(".donation-button", "donation.button");
    setTranslatedText(".modal-title", "donation.modalTitle");
    setTranslatedText(".modal-description", "donation.modalDescription");

    // 푸터
    setTranslatedText(".copyright", "footer.copyright");
    setTranslatedText(".contact", "footer.contact");

    // 언어 스위치 버튼
    select(".lang-switch").textContent =
        currentLanguage === "ko" ? "한국어" : "English";
}

// 언어 변경 함수
function changeLanguage(language) {
    if (language === currentLanguage) return;

    currentLanguage = language;
    localStorage.setItem("language", language);
    translatePage();
}

// 모달 관련 함수
let isModalOpen = false;

function openModal() {
    if (isModalOpen) return;

    const modalOverlay = document.createElement("div");
    modalOverlay.className = "modal-overlay";

    modalOverlay.innerHTML = `
    <div class="modal-content">
      <button class="modal-close">&times;</button>
      <h2 class="modal-title">${translations[currentLanguage].donation.modalTitle}</h2>
      <div class="modal-body">
        <div class="qr-container">
          <img src="/static/images/kakao-qr.png" alt="KakaoPay QR Code" width="250">
          <div class="qr-glass-effect"></div>
        </div>
        <p class="modal-description">${translations[currentLanguage].donation.modalDescription}</p>
      </div>
    </div>
  `;

    document.body.appendChild(modalOverlay);
    document.body.style.overflow = "hidden";

    // 애니메이션 효과
    setTimeout(() => {
        select(".modal-content").classList.add("fade-in");
    }, 10);

    // 닫기 이벤트 설정
    select(".modal-close").addEventListener("click", closeModal);
    modalOverlay.addEventListener("click", (e) => {
        if (e.target === modalOverlay) closeModal();
    });

    isModalOpen = true;
}

function closeModal() {
    if (!isModalOpen) return;

    const modalOverlay = select(".modal-overlay");
    if (modalOverlay) {
        document.body.removeChild(modalOverlay);
        document.body.style.overflow = "";
    }

    isModalOpen = false;
}

// 스크롤 애니메이션
function handleScrollAnimations() {
    const elements = selectAll(".animate-on-scroll");

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("slide-up");
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.1 }
    );

    elements.forEach((el) => observer.observe(el));
}

// 3D 효과 (테슬라 모델)
function createTeslaModel() {
    const container = select(".tesla-model-container");
    if (!container) return;

    // 간단한 Canvas 기반 애니메이션
    const canvas = document.createElement("canvas");
    canvas.width = container.offsetWidth;
    canvas.height = container.offsetHeight;
    container.appendChild(canvas);

    const ctx = canvas.getContext("2d");

    // 테슬라 모델 Y 실루엣 그리기 (간단한 2D 버전)
    function drawTesla(x, y, scale) {
        ctx.save();
        ctx.translate(x, y);
        ctx.scale(scale, scale);

        ctx.beginPath();

        // 차체
        ctx.moveTo(-50, 10);
        ctx.lineTo(-40, 0);
        ctx.lineTo(-20, -10);
        ctx.lineTo(20, -10);
        ctx.lineTo(40, 0);
        ctx.lineTo(50, 10);
        ctx.lineTo(50, 20);
        ctx.lineTo(-50, 20);
        ctx.closePath();

        ctx.fillStyle = "#2271B3";
        ctx.fill();

        // 창문
        ctx.beginPath();
        ctx.moveTo(-30, 0);
        ctx.lineTo(-15, -5);
        ctx.lineTo(15, -5);
        ctx.lineTo(30, 0);
        ctx.lineTo(30, 10);
        ctx.lineTo(-30, 10);
        ctx.closePath();

        ctx.fillStyle = "#aaddff";
        ctx.fill();

        // 바퀴
        ctx.beginPath();
        ctx.arc(-30, 20, 8, 0, Math.PI * 2);
        ctx.fillStyle = "#111";
        ctx.fill();

        ctx.beginPath();
        ctx.arc(30, 20, 8, 0, Math.PI * 2);
        ctx.fillStyle = "#111";
        ctx.fill();

        ctx.restore();
    }

    let angle = 0;

    function animate() {
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // 그림자 효과
        ctx.beginPath();
        ctx.ellipse(centerX, centerY + 60, 70, 15, 0, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(0, 0, 0, 0.1)";
        ctx.fill();

        // 테슬라 모델 그리기 (약간의 움직임 추가)
        const scale = 2 + Math.sin(angle) * 0.1;
        const offsetY = Math.sin(angle * 1.5) * 5;

        drawTesla(centerX, centerY + offsetY, scale);

        angle += 0.02;
        requestAnimationFrame(animate);
    }

    animate();
}

// 카카오페이 QR 코드 3D 효과
function animate3DQRCode() {
    const container = select(".qr-container");
    if (!container) return;

    container.addEventListener("mousemove", (e) => {
        const rect = container.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        const moveX = ((x - centerX) / centerX) * 10;
        const moveY = ((y - centerY) / centerY) * 10;

        container.style.transform = `perspective(1000px) rotateX(${-moveY}deg) rotateY(${moveX}deg) scale3d(1.05, 1.05, 1.05)`;
    });

    container.addEventListener("mouseleave", () => {
        container.style.transform =
            "perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)";
    });
}

// 페이지 로드 시 실행
document.addEventListener("DOMContentLoaded", () => {
    // 언어 설정
    translatePage();

    // 페이지 구성
    const body = document.body;

    // 메인 레이아웃 구성
    const root = select("#root");
    root.innerHTML = `
    <!-- 헤더 -->
    <header class="header">
      <div class="container header-container">
        <a href="#" class="logo">
          <img src="/static/images/tesla-logo.svg" alt="Tesla Alarm Logo">
          <span>Tesla Alarm KR</span>
        </a>
        <nav class="nav-links">
          <a href="#features" class="nav-features">기능</a>
          <a href="#donate" class="nav-donate">후원하기</a>
        </nav>
        <div class="header-actions">
          <button class="lang-switch">${
              currentLanguage === "ko" ? "한국어" : "English"
          }</button>
          <a href="https://t.me/teslalarmKR" target="_blank" class="action-button hero-join-button">텔레그램 채널 참여하기</a>
        </div>
      </div>
    </header>

    <!-- 히어로 섹션 -->
    <section class="hero-section" id="home">
      <div class="container hero-container">
        <h1 class="hero-title animate-on-scroll">테슬라 뉴스와 정보를 실시간으로</h1>
        <p class="hero-description animate-on-scroll">
          테슬라 관련 최신 뉴스, 가격 변동, 보조금 정보까지 AI가 분석하여 신뢰도 높은 정보만 제공합니다.
        </p>
        <div class="hero-buttons animate-on-scroll">
          <a href="https://t.me/teslalarmKR" target="_blank" class="action-button hero-join-button">텔레그램 채널 참여하기</a>
          <a href="#features" class="action-button hero-learn-button" style="background: transparent; border: 1px solid var(--primary-color); color: var(--primary-color);">자세히 알아보기</a>
        </div>
        <div class="tesla-model-container animate-on-scroll"></div>
        <div class="glass-bg glass-bg-1"></div>
        <div class="glass-bg glass-bg-2"></div>
      </div>
    </section>

    <!-- 기능 섹션 -->
    <section class="features-section" id="features">
      <div class="container">
        <h2 class="section-title features-title animate-on-scroll">주요 기능</h2>
        <div class="features-grid">
          <div class="feature-card glass-card feature-realtime animate-on-scroll">
            <div class="feature-icon">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 class="feature-title">실시간 소식</h3>
            <p class="feature-description">테슬라 관련 뉴스를 국내외 신뢰할 수 있는 매체에서 수집하여 제공합니다.</p>
          </div>
          <div class="feature-card glass-card feature-ai animate-on-scroll">
            <div class="feature-icon">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 class="feature-title">AI 신뢰도 분석</h3>
            <p class="feature-description">최첨단 AI 기술로 수집된 정보의 신뢰도를 분석하고 검증된 정보만 제공합니다.</p>
          </div>
          <div class="feature-card glass-card feature-subsidy animate-on-scroll">
            <div class="feature-icon">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 class="feature-title">보조금 정보</h3>
            <p class="feature-description">지역별 전기차 보조금 정보를 실시간으로 업데이트하여 알려드립니다.</p>
          </div>
          <div class="feature-card glass-card feature-community animate-on-scroll">
            <div class="feature-icon">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z" />
              </svg>
            </div>
            <h3 class="feature-title">커뮤니티 정보</h3>
            <p class="feature-description">유용한 테슬라 사용자 팁과 정보를 품질 검증 후 제공합니다.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 후원 섹션 -->
    <section class="donation-section" id="donate">
      <div class="container">
        <h2 class="section-title donation-title animate-on-scroll">프로젝트 후원하기</h2>
        <p class="donation-description animate-on-scroll">
          테슬라 알람 KR은 여러분의 후원으로 더 나은 서비스를 제공할 수 있습니다. 카카오페이로 간편하게 후원해 주세요.
        </p>
        <button class="donation-button animate-on-scroll">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM11 19.93C7.05 19.44 4 16.08 4 12C4 7.92 7.05 4.56 11 4.07V19.93ZM13 4.07C16.95 4.56 20 7.92 20 12C20 16.08 16.95 19.44 13 19.93V4.07Z"/>
          </svg>
          <span>카카오페이로 후원하기</span>
        </button>
      </div>
    </section>

    <!-- 푸터 -->
    <footer class="footer">
      <div class="container footer-container">
        <div class="footer-links">
          <a href="#" class="contact">문의사항</a>
        </div>
        <div class="social-links">
          <a href="https://t.me/teslalarmKR" target="_blank" class="social-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
              <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM8.287 5.906c-.778.324-2.334.994-4.666 2.01-.378.15-.577.298-.595.442-.03.243.275.339.69.47l.175.055c.408.133.958.288 1.243.294.26.006.549-.1.868-.32 2.179-1.471 3.304-2.214 3.374-2.23.05-.012.12-.026.166.016.047.041.042.12.037.141-.03.129-1.227 1.241-1.846 1.817-.193.18-.33.307-.358.336a8.154 8.154 0 0 1-.188.186c-.38.366-.664.64.015 1.088.327.216.589.393.85.571.284.194.568.387.936.629.093.06.183.125.27.187.331.236.63.448.997.414.214-.02.435-.22.547-.82.265-1.417.786-4.486.906-5.751a1.426 1.426 0 0 0-.013-.315.337.337 0 0 0-.114-.217.526.526 0 0 0-.31-.093c-.3.005-.763.166-2.984 1.09z"/>
            </svg>
          </a>
          <a href="https://github.com/devkoriel/teslalarm-kr" target="_blank" class="social-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
              <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
            </svg>
          </a>
        </div>
        <p class="copyright">© 2024 테슬라 알람 KR. All rights reserved.</p>
      </div>
    </footer>
  `;

    // 이벤트 리스너 설정
    select(".lang-switch").addEventListener("click", () => {
        changeLanguage(currentLanguage === "ko" ? "en" : "ko");
    });

    select(".donation-button").addEventListener("click", openModal);

    // 애니메이션 효과 초기화
    handleScrollAnimations();

    // 테슬라 모델 애니메이션
    createTeslaModel();

    // fetch API 정보
    fetch("/api/info")
        .then((response) => response.json())
        .then((data) => {
            // API 데이터 활용 (필요시)
            console.log("API 정보:", data);
        })
        .catch((error) => {
            console.error("API 요청 오류:", error);
        });
});

// 카카오페이 QR 코드 3D 효과 이벤트 리스너
document.addEventListener("click", (e) => {
    if (e.target.closest(".qr-container")) {
        animate3DQRCode();
    }
});

// 스크롤 이벤트 처리
window.addEventListener("scroll", () => {
    const header = select(".header");
    if (window.scrollY > 50) {
        header.style.boxShadow = "0 4px 10px rgba(0, 0, 0, 0.05)";
    } else {
        header.style.boxShadow = "none";
    }
});
