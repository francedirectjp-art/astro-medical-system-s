// フォーム検証とローディング処理
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('astroForm');
    const submitBtn = document.getElementById('submitBtn');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const loadingMessage = document.getElementById('loadingMessage');
    const progressBar = document.getElementById('progressBar');

    // ローディングメッセージのバリエーション
    const loadingMessages = [
        'あなたの宇宙的な体質を分析しています...',
        '天体の配置を計算中...',
        '太陽と月の位置を確認しています...',
        '惑星のアスペクトを解析中...',
        '四元素のバランスを調べています...',
        '16原型との共鳴を確認中...',
        'まもなく完了します...'
    ];

    // フォーム送信時の処理
    if (form) {
        form.addEventListener('submit', function(e) {
            // フォームのバリデーション
            if (!validateForm()) {
                e.preventDefault();
                return false;
            }

            // ローディング画面を表示
            showLoading();

            // ローディングメッセージを順番に表示
            let messageIndex = 0;
            const messageInterval = setInterval(() => {
                if (messageIndex < loadingMessages.length) {
                    loadingMessage.textContent = loadingMessages[messageIndex];
                    messageIndex++;
                } else {
                    clearInterval(messageInterval);
                }
            }, 1500);
        });
    }

    // フォームバリデーション
    function validateForm() {
        const name = document.getElementById('name').value.trim();
        const birthYear = document.getElementById('birth_year').value;
        const birthMonth = document.getElementById('birth_month').value;
        const birthDay = document.getElementById('birth_day').value;
        const birthHour = document.getElementById('birth_hour').value;
        const birthMinute = document.getElementById('birth_minute').value;
        const prefecture = document.getElementById('prefecture').value;

        // 名前のバリデーション
        if (!name) {
            showError('お名前を入力してください');
            document.getElementById('name').focus();
            return false;
        }

        // 年のバリデーション
        if (!birthYear || birthYear < 1900 || birthYear > 2030) {
            showError('正しい生年を入力してください（1900-2030）');
            document.getElementById('birth_year').focus();
            return false;
        }

        // 月のバリデーション
        if (!birthMonth) {
            showError('生月を選択してください');
            document.getElementById('birth_month').focus();
            return false;
        }

        // 日のバリデーション
        const maxDay = new Date(birthYear, birthMonth, 0).getDate();
        if (!birthDay || birthDay < 1 || birthDay > maxDay) {
            showError(`正しい生日を入力してください（1-${maxDay}）`);
            document.getElementById('birth_day').focus();
            return false;
        }

        // 時刻のバリデーション
        if (birthHour === '') {
            showError('出生時刻（時）を選択してください');
            document.getElementById('birth_hour').focus();
            return false;
        }

        if (birthMinute === '') {
            showError('出生時刻（分）を選択してください');
            document.getElementById('birth_minute').focus();
            return false;
        }

        // 都道府県のバリデーション
        if (!prefecture) {
            showError('出生地の都道府県を選択してください');
            document.getElementById('prefecture').focus();
            return false;
        }

        return true;
    }

    // エラーメッセージ表示
    function showError(message) {
        // 既存のエラーメッセージを削除
        const existingError = document.querySelector('.error-toast');
        if (existingError) {
            existingError.remove();
        }

        // エラートーストを作成
        const errorToast = document.createElement('div');
        errorToast.className = 'error-toast';
        errorToast.innerHTML = `
            <span class="error-icon">⚠️</span>
            <span>${message}</span>
        `;
        document.body.appendChild(errorToast);

        // 3秒後に自動的に削除
        setTimeout(() => {
            errorToast.classList.add('fade-out');
            setTimeout(() => errorToast.remove(), 300);
        }, 3000);
    }

    // ローディング画面表示
    function showLoading() {
        if (loadingOverlay) {
            loadingOverlay.style.display = 'flex';
            // プログレスバーアニメーション開始
            if (progressBar) {
                progressBar.style.animation = 'progress 10s ease-in-out forwards';
            }
        }
    }

    // 日付の最大値を動的に設定
    const birthDayInput = document.getElementById('birth_day');
    const birthMonthSelect = document.getElementById('birth_month');
    const birthYearInput = document.getElementById('birth_year');

    function updateMaxDay() {
        if (birthDayInput && birthMonthSelect && birthYearInput) {
            const year = birthYearInput.value || new Date().getFullYear();
            const month = birthMonthSelect.value || 1;
            const maxDay = new Date(year, month, 0).getDate();
            birthDayInput.max = maxDay;
            
            // 現在の値が最大値を超えている場合は調整
            if (birthDayInput.value > maxDay) {
                birthDayInput.value = maxDay;
            }
        }
    }

    if (birthMonthSelect) {
        birthMonthSelect.addEventListener('change', updateMaxDay);
    }
    if (birthYearInput) {
        birthYearInput.addEventListener('change', updateMaxDay);
    }

    // 名前入力時のリアルタイムフィードバック
    const nameInput = document.getElementById('name');
    if (nameInput) {
        nameInput.addEventListener('input', function() {
            const value = this.value.trim();
            if (value.length > 0) {
                this.classList.add('valid');
                this.classList.remove('invalid');
            } else {
                this.classList.remove('valid');
            }
        });
    }

    // 入力フィールドのフォーカス時エフェクト
    const inputs = document.querySelectorAll('.form-input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
            if (this.value) {
                this.classList.add('has-value');
            } else {
                this.classList.remove('has-value');
            }
        });
    });

    // スムーズスクロール
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// エラートーストのスタイル
const style = document.createElement('style');
style.textContent = `
    .error-toast {
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(255, 107, 107, 0.95);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        display: flex;
        align-items: center;
        gap: 0.5rem;
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
        max-width: 400px;
    }

    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    .error-toast.fade-out {
        animation: fadeOut 0.3s ease-out forwards;
    }

    @keyframes fadeOut {
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }

    .form-input.valid {
        border-color: #51cf66;
    }

    .form-input.invalid {
        border-color: #ff6b6b;
    }

    .form-group.focused .form-label {
        color: var(--primary-gold);
    }

    @media (max-width: 480px) {
        .error-toast {
            right: 10px;
            left: 10px;
            max-width: calc(100% - 20px);
        }
    }
`;
document.head.appendChild(style);