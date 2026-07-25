/* Modern Offline Jalali (Shamsi) DatePicker JS Library */
(function() {
    'use strict';

    function toFarsiNumber(n) {
        if (n === null || n === undefined) return '';
        const farsiDigits = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
        return n.toString().replace(/\d/g, x => farsiDigits[x]);
    }

    function toEnglishNumber(s) {
        if (!s) return '';
        const farsiDigits = [/۰/g, /۱/g, /۲/g, /۳/g, /۴/g, /۵/g, /۶/g, /۷/g, /۸/g, /۹/g];
        let str = s.toString();
        for (let i = 0; i < 10; i++) {
            str = str.replace(farsiDigits[i], i);
        }
        return str;
    }

    // Gregorian to Jalali conversion
    function g2j(gy, gm, gd) {
        var g_d_m = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
        var gy2 = (gm > 2) ? (gy + 1) : gy;
        var days = 355666 + (365 * gy) + Math.floor((gy2 + 3) / 4) - Math.floor((gy2 + 99) / 100) + Math.floor((gy2 + 399) / 400) + gd;
        for (var i = 0; i < gm; ++i) days += g_d_m[i];
        var jy = -1595 + (33 * Math.floor(days / 12053));
        days %= 12053;
        jy += 4 * Math.floor(days / 1461);
        days %= 1461;
        if (days > 365) {
            jy += Math.floor((days - 1) / 365);
            days = (days - 1) % 365;
        }
        var jm = (days < 186) ? 1 + Math.floor(days / 31) : 7 + Math.floor((days - 186) / 30);
        var jd = (days < 186) ? 1 + (days % 31) : 1 + ((days - 186) % 30);
        return [jy, jm, jd];
    }

    // Jalali to Gregorian conversion
    function j2g(jy, jm, jd) {
        var jy_calc = jy + 1595;
        var days = -355668 + (365 * jy_calc) + Math.floor(jy_calc / 33) * 8 + Math.floor(((jy_calc % 33) + 3) / 4) + jd;
        days += (jm < 7) ? (jm - 1) * 31 : ((jm - 7) * 30) + 186;
        var gy = 400 * Math.floor(days / 146097);
        days %= 146097;
        if (days > 36524) {
            gy += 100 * Math.floor(--days / 36524);
            days %= 36524;
            if (days >= 365) days++;
        }
        gy += 4 * Math.floor(days / 1461);
        days %= 1461;
        if (days > 365) {
            gy += Math.floor((days - 1) / 365);
            days = (days - 1) % 365;
        }
        var gd = days + 1;
        var sal_a = [0, 31, ((gy % 4 === 0 && gy % 100 !== 0) || (gy % 400 === 0)) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
        var gm = 0;
        for (gm = 0; gm < 13 && gd > sal_a[gm]; gm++) gd -= sal_a[gm];
        return [gy, gm, gd];
    }

    function isJalaliLeapYear(jy) {
        var g = j2g(jy, 12, 30);
        var j = g2j(g[0], g[1], g[2]);
        return (j[0] === jy && j[1] === 12 && j[2] === 30);
    }

    function getJalaliMonthDays(jy, jm) {
        if (jm <= 6) return 31;
        if (jm <= 11) return 30;
        return isJalaliLeapYear(jy) ? 30 : 29;
    }

    function getFirstWeekdayOfMonth(jy, jm) {
        var g = j2g(jy, jm, 1);
        var d = new Date(g[0], g[1] - 1, g[2]).getDay(); // 0=Sunday
        return (d + 1) % 7; // 0=Saturday
    }

    const jalaliMonths = [
        'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
        'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
    ];

    let currentPicker = null;

    class JalaliDatePicker {
        constructor(input) {
            this.input = input;
            this.container = null;
            const now = new Date();
            this.todayJalali = g2j(now.getFullYear(), now.getMonth() + 1, now.getDate());
            this.viewYear = this.todayJalali[0];
            this.viewMonth = this.todayJalali[1];
            this.selectedYear = null;
            this.selectedMonth = null;
            this.selectedDay = null;

            this.init();
        }

        init() {
            this.input.setAttribute('autocomplete', 'off');
            this.input.addEventListener('focus', () => this.show());
            this.input.addEventListener('click', () => this.show());

            document.addEventListener('click', (e) => {
                if (this.container && !this.container.contains(e.target) && e.target !== this.input) {
                    this.hide();
                }
            });

            window.addEventListener('resize', () => {
                if (this.container && this.container.style.display === 'block') {
                    this.positionDOM();
                }
            });
        }

        parseInputValue() {
            let val = toEnglishNumber(this.input.value).trim();
            if (val) {
                let parts = val.split(/[\/\-]/);
                if (parts.length === 3) {
                    let y = parseInt(parts[0], 10);
                    let m = parseInt(parts[1], 10);
                    let d = parseInt(parts[2], 10);
                    if (y > 1300 && y < 1500 && m >= 1 && m <= 12 && d >= 1 && d <= 31) {
                        this.selectedYear = y;
                        this.selectedMonth = m;
                        this.selectedDay = d;
                        this.viewYear = y;
                        this.viewMonth = m;
                        return;
                    }
                }
            }
            this.selectedYear = null;
            this.selectedMonth = null;
            this.selectedDay = null;
        }

        show() {
            if (currentPicker && currentPicker !== this) {
                currentPicker.hide();
            }
            currentPicker = this;

            this.parseInputValue();

            if (!this.container) {
                this.createDOM();
            }
            this.render();
            this.positionDOM();
            this.container.style.display = 'block';
        }

        hide() {
            if (this.container) {
                this.container.style.display = 'none';
            }
        }

        positionDOM() {
            const rect = this.input.getBoundingClientRect();
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;

            this.container.style.top = (rect.bottom + scrollTop + 4) + 'px';
            this.container.style.left = (rect.left + scrollLeft) + 'px';
        }

        createDOM() {
            this.container = document.createElement('div');
            this.container.className = 'jdp-container';
            document.body.appendChild(this.container);
        }

        render() {
            this.container.innerHTML = '';

            // Header
            const header = document.createElement('div');
            header.className = 'jdp-header';

            const prevBtn = document.createElement('button');
            prevBtn.className = 'jdp-nav-btn';
            prevBtn.type = 'button';
            prevBtn.innerHTML = '‹';
            prevBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.prevMonth();
            });

            const nextBtn = document.createElement('button');
            nextBtn.className = 'jdp-nav-btn';
            nextBtn.type = 'button';
            nextBtn.innerHTML = '›';
            nextBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.nextMonth();
            });

            const monthSelect = document.createElement('select');
            jalaliMonths.forEach((mName, idx) => {
                const opt = document.createElement('option');
                opt.value = idx + 1;
                opt.textContent = mName;
                if (idx + 1 === this.viewMonth) opt.selected = true;
                monthSelect.appendChild(opt);
            });
            monthSelect.addEventListener('change', (e) => {
                this.viewMonth = parseInt(e.target.value, 10);
                this.render();
            });

            const yearSelect = document.createElement('select');
            for (let y = 1380; y <= 1430; y++) {
                const opt = document.createElement('option');
                opt.value = y;
                opt.textContent = toFarsiNumber(y);
                if (y === this.viewYear) opt.selected = true;
                yearSelect.appendChild(opt);
            }
            yearSelect.addEventListener('change', (e) => {
                this.viewYear = parseInt(e.target.value, 10);
                this.render();
            });

            const selectGroup = document.createElement('div');
            selectGroup.style.display = 'flex';
            selectGroup.style.gap = '4px';
            selectGroup.appendChild(monthSelect);
            selectGroup.appendChild(yearSelect);

            header.appendChild(nextBtn);
            header.appendChild(selectGroup);
            header.appendChild(prevBtn);

            this.container.appendChild(header);

            // Weekdays
            const weekdays = document.createElement('div');
            weekdays.className = 'jdp-weekdays';
            ['ش', '۱ش', '۲ش', '۳ش', '۴ش', '۵ش', 'ج'].forEach(w => {
                const div = document.createElement('div');
                div.textContent = w;
                weekdays.appendChild(div);
            });
            this.container.appendChild(weekdays);

            // Days Grid
            const daysContainer = document.createElement('div');
            daysContainer.className = 'jdp-days';

            const firstWeekday = getFirstWeekdayOfMonth(this.viewYear, this.viewMonth);
            const totalDays = getJalaliMonthDays(this.viewYear, this.viewMonth);

            // Empty slots
            for (let i = 0; i < firstWeekday; i++) {
                const empty = document.createElement('div');
                empty.className = 'jdp-day empty';
                daysContainer.appendChild(empty);
            }

            // Month days
            for (let d = 1; d <= totalDays; d++) {
                const dayDiv = document.createElement('div');
                dayDiv.className = 'jdp-day';
                dayDiv.textContent = toFarsiNumber(d);

                if (this.viewYear === this.todayJalali[0] && this.viewMonth === this.todayJalali[1] && d === this.todayJalali[2]) {
                    dayDiv.classList.add('today');
                }

                if (this.selectedYear === this.viewYear && this.selectedMonth === this.viewMonth && this.selectedDay === d) {
                    dayDiv.classList.add('selected');
                }

                dayDiv.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.selectDay(d);
                });

                daysContainer.appendChild(dayDiv);
            }

            this.container.appendChild(daysContainer);

            // Footer
            const footer = document.createElement('div');
            footer.className = 'jdp-footer';

            const todayBtn = document.createElement('button');
            todayBtn.className = 'jdp-today-btn';
            todayBtn.type = 'button';
            todayBtn.textContent = 'امروز';
            todayBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.viewYear = this.todayJalali[0];
                this.viewMonth = this.todayJalali[1];
                this.selectDay(this.todayJalali[2]);
            });

            const clearBtn = document.createElement('button');
            clearBtn.className = 'jdp-clear-btn';
            clearBtn.type = 'button';
            clearBtn.textContent = 'پاک کردن';
            clearBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.input.value = '';
                this.hide();
            });

            footer.appendChild(todayBtn);
            footer.appendChild(clearBtn);
            this.container.appendChild(footer);
        }

        prevMonth() {
            if (this.viewMonth === 1) {
                this.viewMonth = 12;
                this.viewYear--;
            } else {
                this.viewMonth--;
            }
            this.render();
        }

        nextMonth() {
            if (this.viewMonth === 12) {
                this.viewMonth = 1;
                this.viewYear++;
            } else {
                this.viewMonth++;
            }
            this.render();
        }

        selectDay(day) {
            this.selectedYear = this.viewYear;
            this.selectedMonth = this.viewMonth;
            this.selectedDay = day;

            let mStr = this.selectedMonth < 10 ? '0' + this.selectedMonth : '' + this.selectedMonth;
            let dStr = this.selectedDay < 10 ? '0' + this.selectedDay : '' + this.selectedDay;

            let formatted = `${this.selectedYear}/${mStr}/${dStr}`;
            this.input.value = toFarsiNumber(formatted);

            this.input.dispatchEvent(new Event('input', { bubbles: true }));
            this.input.dispatchEvent(new Event('change', { bubbles: true }));

            this.hide();
        }
    }

    window.initJalaliDatePicker = function() {
        const selectors = '.jalali-date-input, input[type="text"][name*="date"], input[type="text"][id*="date"]';
        document.querySelectorAll(selectors).forEach(input => {
            if (!input.dataset.jdpInit) {
                input.dataset.jdpInit = 'true';
                new JalaliDatePicker(input);
            }
        });
    };

    document.addEventListener('DOMContentLoaded', function() {
        window.initJalaliDatePicker();
    });

})();
