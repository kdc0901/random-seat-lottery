import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import os
import math
import json
from datetime import datetime

class LotteryApp:
    # 클래스 상수 정의
    CANVAS_WIDTH = 1000
    CANVAS_HEIGHT = 900
    BOARD_WIDTH = 300
    BOARD_HEIGHT = 50
    SEAT_WIDTH = 28  # 숫자 표시용 (안쪽 원)
    SEAT_HEIGHT = 28
    NAME_WIDTH = 80  # 이름 표시용 (바깥쪽 원)
    NAME_HEIGHT = 26  # 이름칸 높이 축소
    MAX_SEATS = 43
    
    # 좌석 배치 관련 상수
    CENTER_Y_OFFSET = 50
    INNER_RADIUS = 250  # 숫자 표시용 안쪽 원 반지름
    OUTER_RADIUS = 290  # 이름 표시용 바깥쪽 원 반지름 (더 가깝게 조정)
    
    # 그룹 정의
    GROUPS = {
        'A': range(37, 44),  # 37-43번
        'B': range(31, 37),  # 31-36번
        'C': range(25, 31),  # 25-30번
        'D': range(19, 25),  # 19-24번
        'E': range(13, 19),  # 13-18번
        'F': range(7, 13),   # 7-12번
        'G': range(1, 7)     # 1-6번
    }
    
    # 그룹별 색상 (더 선명한 색상으로 변경)
    GROUP_COLORS = {
        'A': '#FFB6C1',  # 연한 분홍
        'B': '#98FB98',  # 연한 초록
        'C': '#87CEEB',  # 하늘색
        'D': '#DDA0DD',  # 연한 보라
        'E': '#F0E68C',  # 카키색
        'F': '#E0FFFF',  # 연한 청록
        'G': '#FFA07A',  # 연한 살몬
        'H': '#FFE4B5',  # 모카색
        'I': '#B0E0E6',  # 파우더블루
        'J': '#DEB887',  # 버블우드
        'K': '#98FF98'   # 민트크림
    }
    
    # 결과 저장 파일 경로
    HISTORY_FILE = "lottery_history.json"
    
    def __init__(self, root):
        self.root = root
        self.root.title("자리 배치 프로그램")
        self.root.geometry("1100x800")
        
        # 결과 저장용 변수
        self.current_results = []
        self.previous_results = self.load_previous_results()
        self.is_grouped = True  # 기본적으로 그룹 표시 활성화
        self.group_size = 6  # 기본 그룹 크기
        
        self._init_ui()
        
        # 테스트를 위한 자동 데이터 로드
        self._load_test_data()
        
    def _init_ui(self):
        """UI 초기화"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 좌측 프레임 (입력 영역)
        left_frame = ttk.Frame(main_frame, width=400)
        left_frame.pack(side="left", fill="both", expand=True, padx=5)

        # 우측 프레임 (자리 배치도)
        right_frame = ttk.Frame(main_frame, width=self.CANVAS_WIDTH)
        right_frame.pack(side="right", fill="both", expand=True, padx=5)

        self._init_input_area(left_frame)
        self._init_canvas(right_frame)

    def _init_input_area(self, parent):
        """입력 영역 초기화"""
        # 상단 버튼 프레임
        top_button_frame = ttk.Frame(parent)
        top_button_frame.pack(fill="x", pady=5)

        # 엑셀 파일 불러오기 버튼
        self.load_excel_button = ttk.Button(top_button_frame, text="엑셀 파일 불러오기", command=self.load_excel)
        self.load_excel_button.pack(side="left", padx=5)

        # 이름 입력 프레임
        self.input_frame = ttk.LabelFrame(parent, text="참가자 이름 입력", padding="10")
        self.input_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 스크롤바와 캔버스 설정
        self.canvas = tk.Canvas(self.input_frame)
        scrollbar = ttk.Scrollbar(self.input_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # 입력 필드 생성
        self.name_entries = []
        for i in range(self.MAX_SEATS):
            entry_frame = ttk.Frame(self.scrollable_frame)
            entry_frame.pack(fill="x", padx=5, pady=2)
            
            label = ttk.Label(entry_frame, text=f"{i+1:2d}번:", width=5)
            label.pack(side="left")
            
            entry = ttk.Entry(entry_frame, width=30)
            entry.pack(side="left", fill="x", expand=True, padx=(5, 10))
            self.name_entries.append(entry)

        # 스크롤바와 캔버스 배치
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # 버튼 프레임
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=10)

        # 그룹 크기 입력 프레임
        group_frame = ttk.Frame(button_frame)
        group_frame.pack(side="left", padx=5)
        
        ttk.Label(group_frame, text="그룹 크기:").pack(side="left")
        self.group_size_var = tk.StringVar(value="6")
        self.group_size_entry = ttk.Entry(group_frame, width=5, textvariable=self.group_size_var)
        self.group_size_entry.pack(side="left", padx=5)
        
        # 그룹으로 묶기 버튼
        self.group_button = ttk.Button(button_frame, text="그룹으로 묶기", command=self.toggle_groups)
        self.group_button.pack(side="right", padx=5)

        # 추첨 버튼
        self.draw_button = ttk.Button(button_frame, text="자리 배치하기", command=self.draw_lots)
        self.draw_button.pack(side="right", padx=5)

        # 초기화 버튼
        self.clear_button = ttk.Button(button_frame, text="초기화", command=self.clear_entries)
        self.clear_button.pack(side="right", padx=5)

        # 마우스 휠 바인딩
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _init_canvas(self, parent):
        """캔버스 초기화"""
        self.seat_canvas = tk.Canvas(parent, 
                                   width=self.CANVAS_WIDTH, 
                                   height=self.CANVAS_HEIGHT, 
                                   bg='white')
        self.seat_canvas.pack(padx=10, pady=10)

    def _on_mousewheel(self, event):
        """마우스 휠 이벤트 처리"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def clear_entries(self):
        """입력 필드와 캔버스 초기화"""
        for entry in self.name_entries:
            entry.delete(0, tk.END)
        self.seat_canvas.delete("all")
        self.current_results = []

    def load_excel(self):
        """엑셀 파일에서 이름 불러오기"""
        file_path = filedialog.askopenfilename(
            title="엑셀 파일 선택",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        
        if not file_path:
            return

        try:
            df = pd.read_excel(file_path)
            names = df.iloc[:, 1].dropna().tolist()
            self.clear_entries()
            
            for i, name in enumerate(names):
                if i < self.MAX_SEATS:
                    self.name_entries[i].insert(0, str(name))
            
            messagebox.showinfo("성공", f"총 {min(len(names), self.MAX_SEATS)}개의 이름이 입력되었습니다.")
            
        except Exception as e:
            messagebox.showerror("오류", f"엑셀 파일을 읽는 중 오류가 발생했습니다:\n{str(e)}")

    def draw_seat(self, number, name, angle, inner_x, inner_y, outer_x, outer_y):
        """개별 좌석 그리기 (이중 원형)"""
        # 그룹 색상 설정
        current_groups = self.get_groups_from_size(len(self.current_results))
        group = None
        for g, number_range in current_groups.items():
            if number in number_range:
                group = g
                break
        
        fill_color = self.GROUP_COLORS[group] if self.is_grouped and group else "#E3F2FD"
        
        # 연결선 먼저 그리기 (가장 아래 레이어)
        line_color = "#1976D2"  # 기본 파란색
        if self.is_grouped and group:
            line_color = self.GROUP_COLORS[group]
        
        # 연결선 시작점과 끝점 조정 (원과 사각형 경계에 맞춤)
        angle_rad = math.atan2(outer_y - inner_y, outer_x - inner_x)
        start_x = inner_x + (self.SEAT_WIDTH/2) * math.cos(angle_rad)
        start_y = inner_y + (self.SEAT_WIDTH/2) * math.sin(angle_rad)
        end_x = outer_x - (self.NAME_HEIGHT/2) * math.cos(angle_rad)
        end_y = outer_y - (self.NAME_HEIGHT/2) * math.sin(angle_rad)
        
        self.seat_canvas.create_line(
            start_x, start_y,
            end_x, end_y,
            fill=line_color,
            width=1
        )
        
        # 안쪽 원: 숫자 표시
        self.seat_canvas.create_oval(
            inner_x - self.SEAT_WIDTH/2, inner_y - self.SEAT_HEIGHT/2,
            inner_x + self.SEAT_WIDTH/2, inner_y + self.SEAT_HEIGHT/2,
            fill=fill_color,
            outline="#1976D2",
            width=1.5
        )
        
        # 숫자 텍스트
        self.seat_canvas.create_text(
            inner_x, inner_y,
            text=str(number),
            font=('Arial', 12, 'bold'),
            fill='#1976D2'
        )
        
        # 바깥 원: 이름 표시
        name_width = min(len(name) * 11 + 10, self.NAME_WIDTH)
        name_height = self.NAME_HEIGHT
        
        # 이름 배경
        self.seat_canvas.create_rectangle(
            outer_x - name_width/2, outer_y - name_height/2,
            outer_x + name_width/2, outer_y + name_height/2,
            fill='white',
            outline='#1976D2',
            width=1.5
        )
        
        # 이름 텍스트
        self.seat_canvas.create_text(
            outer_x, outer_y,
            text=name,
            font=('Arial', 11),
            fill='#000000'
        )

    def load_previous_results(self):
        """이전 추첨 결과 불러오기"""
        try:
            if os.path.exists(self.HISTORY_FILE):
                with open(self.HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"이전 결과 로딩 중 오류: {e}")
            return []
            
    def save_current_results(self):
        """현재 추첨 결과 저장"""
        try:
            # 현재 결과를 딕셔너리로 변환
            result_dict = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'combinations': [(num, name) for num, name in self.current_results]
            }
            
            # 이전 결과에 추가
            self.previous_results.append(result_dict)
            
            # 파일에 저장
            with open(self.HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.previous_results, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"결과 저장 중 오류: {e}")

    def is_similar_combination(self, new_combination, previous_combination):
        """두 자리 배치 조합이 유사한지 확인"""
        # 이름 목록이 같고 순서만 다른 경우를 체크
        new_names = set(name for _, name in new_combination)
        prev_names = set(name for _, name in previous_combination)
        return new_names == prev_names

    def get_groups_from_size(self, total_count):
        """그룹 크기에 따라 그룹 범위 계산"""
        try:
            group_size = int(self.group_size_var.get())
            if group_size < 1:
                messagebox.showwarning("경고", "그룹 크기는 1 이상이어야 합니다!")
                return self.GROUPS

            groups = {}
            group_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']  # 그룹 이름 추가
            current_number = 1
            group_index = 0

            while current_number <= total_count and group_index < len(group_names):
                group_end = min(current_number + group_size - 1, total_count)
                groups[group_names[group_index]] = range(current_number, group_end + 1)
                current_number = group_end + 1
                group_index += 1

            return groups
            
        except ValueError:
            messagebox.showwarning("경고", "올바른 그룹 크기를 입력해주세요!")
            return self.GROUPS

    def toggle_groups(self):
        """그룹 표시 토글"""
        if not self.current_results:
            messagebox.showwarning("경고", "먼저 자리 배치를 해주세요!")
            return
            
        self.is_grouped = not self.is_grouped
        self.redraw_seats()

    def redraw_seats(self):
        """자리 배치 다시 그리기 (이중 원형)"""
        self.seat_canvas.delete("all")
        
        # 캔버스 중심점 계산
        center_x = self.CANVAS_WIDTH // 2
        center_y = (self.CANVAS_HEIGHT // 2) + self.CENTER_Y_OFFSET
        
        total_seats = len(self.current_results)
        if total_seats == 0:
            return
        
        # 정보 표시 영역 그리기
        self._draw_info_area(total_seats)
        
        # 칠판 그리기 (42번과 4번 사이 상단)
        board_width = 200
        board_height = 40
        board_y = center_y - self.INNER_RADIUS - 100  # 안쪽 원보다 100px 위쪽에 위치
        
        # 칠판 배경
        self.seat_canvas.create_rectangle(
            center_x - board_width/2, board_y - board_height/2,
            center_x + board_width/2, board_y + board_height/2,
            fill="#2E7D32",  # 진한 초록색
            outline="#81C784",  # 연한 초록색
            width=2
        )
        
        # 칠판 텍스트
        self.seat_canvas.create_text(
            center_x, board_y,
            text="칠판",
            font=('Arial', 16, 'bold'),
            fill='white'
        )
        
        angle_step = 2 * math.pi / total_seats
        start_angle = math.pi / 2  # 12시 방향에서 시작
        
        # 모든 좌석 그리기
        for i, (number, name) in enumerate(self.current_results):
            angle = start_angle - (i * angle_step)
            
            # 안쪽 원의 좌표 (숫자용)
            inner_x = center_x + self.INNER_RADIUS * math.cos(angle)
            inner_y = center_y - self.INNER_RADIUS * math.sin(angle)
            
            # 바깥쪽 원의 좌표 (이름용)
            outer_x = center_x + self.OUTER_RADIUS * math.cos(angle)
            outer_y = center_y - self.OUTER_RADIUS * math.sin(angle)
            
            # 좌석 그리기
            self.draw_seat(number, name, angle, inner_x, inner_y, outer_x, outer_y)

    def draw_lots(self):
        """추첨 및 자리 배치"""
        names = [entry.get().strip() for entry in self.name_entries if entry.get().strip()]
        
        if not names:
            messagebox.showwarning("경고", "최소 1명의 이름을 입력해주세요!")
            return

        # 캔버스 초기화
        self.seat_canvas.delete("all")
        self.current_results = []

        # 최대 시도 횟수 설정
        max_attempts = 100
        attempt = 0
        
        while attempt < max_attempts:
            # 이름 순서를 랜덤하게 섞기
            random.shuffle(names)
            
            # 현재 조합 생성
            temp_results = [(i + 1, name) for i, name in enumerate(names)]
            
            # 이전 결과와 비교
            is_duplicate = False
            for prev_result in self.previous_results:
                if self.is_similar_combination(temp_results, prev_result['combinations']):
                    is_duplicate = True
                    break
            
            # 중복되지 않는 조합을 찾았거나, 최대 시도 횟수에 도달
            if not is_duplicate or attempt == max_attempts - 1:
                self.current_results = temp_results
                break
                
            attempt += 1

        # 결과 표시 전에 그룹 상태 초기화
        self.is_grouped = True  # 기본적으로 그룹 표시 활성화
        
        # 자리 배치 그리기
        self.redraw_seats()
        
        # 결과 저장
        self.save_current_results()
        
        # 결과 표시
        self._show_results()

    def _draw_info_area(self, total_count):
        """정보 표시 영역 그리기"""
        # 총 인원수 표시
        self.seat_canvas.create_text(
            self.CANVAS_WIDTH - 20, 20,
            text=f"총 {total_count}명",
            anchor="e",
            fill="#1B5E20",
            font=('Arial', 14, 'bold')
        )

    def _draw_board(self, center_x):
        """칠판 그리기"""
        # 칠판 배경
        self.seat_canvas.create_rectangle(
            center_x - self.BOARD_WIDTH/2, self.BOARD_TOP,
            center_x + self.BOARD_WIDTH/2, self.BOARD_TOP + self.BOARD_HEIGHT,
            fill="#1B5E20",  # 진한 초록색
            outline="#81C784",  # 연한 초록색
            width=3
        )
        
        # 칠판 텍스트
        self.seat_canvas.create_text(
            center_x, self.BOARD_TOP + self.BOARD_HEIGHT/2,
            text="칠판",
            fill="white",
            font=('Arial', 18, 'bold')
        )

    def _show_results(self):
        """추첨 결과 표시"""
        if not self.current_results:
            return
            
        # 결과 창 생성
        result_window = tk.Toplevel(self.root)
        result_window.title("추첨 결과")
        result_window.geometry("400x600")
        
        # 결과 창을 메인 창의 오른쪽에 위치시키기
        result_window.transient(self.root)  # 부모 창 설정
        result_window.grab_set()  # 모달 창으로 설정
        
        # 창 위치 계산 (메인 창의 오른쪽 끝에서 시작)
        x = self.root.winfo_x() + self.root.winfo_width()
        y = self.root.winfo_y()
        result_window.geometry(f"+{x}+{y}")
        
        # 스타일 설정
        style = ttk.Style()
        style.configure("Result.TLabel", 
                       font=('Arial', 12),
                       padding=(10, 5),
                       background='#E3F2FD')
        
        # 결과 표시 영역
        result_frame = ttk.Frame(result_window, padding="20")
        result_frame.pack(fill="both", expand=True)
        
        # 제목
        title_frame = ttk.Frame(result_frame)
        title_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(title_frame, 
                 text="자리 배치 결과", 
                 font=('Arial', 16, 'bold')).pack(side="left")
        
        ttk.Label(title_frame,
                 text=f"총 {len(self.current_results)}명",
                 font=('Arial', 12)).pack(side="right")
        
        # 결과 목록 프레임 (스크롤 가능)
        canvas = tk.Canvas(result_frame)
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=350)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 결과 목록 (3열로 표시)
        columns = 3
        rows = (len(self.current_results) + columns - 1) // columns
        
        sorted_results = sorted(self.current_results)
        for i in range(rows):
            for j in range(columns):
                idx = i + j * rows
                if idx < len(sorted_results):
                    number, name = sorted_results[idx]
                    frame = ttk.Frame(scrollable_frame)
                    frame.grid(row=i, column=j, padx=5, pady=2, sticky="ew")
                    
                    label = ttk.Label(
                        frame,
                        text=f"{number:2d}번: {name}",
                        style="Result.TLabel"
                    )
                    label.pack(fill="x")
        
        # 스크롤바와 캔버스 배치
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # 닫기 버튼
        button_frame = ttk.Frame(result_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        close_button = ttk.Button(
            button_frame,
            text="닫기",
            command=result_window.destroy,
            width=20
        )
        close_button.pack(side="right")

    def get_group_for_number(self, number):
        """번호에 해당하는 그룹 찾기"""
        for group, number_range in self.GROUPS.items():
            if number in number_range:
                return group
        return None  # 그룹이 없는 경우

    def _load_test_data(self):
        """테스트용 데이터 자동 로드"""
        test_names = [
            "김민수", "이영희", "박철수", "정미경", "강동원", "윤서연",
            "임재현", "한미영", "송지훈", "노은주", "류현진", "백지영",
            "서민호", "최유리", "오태호", "구자경", "남기준", "홍서영",
            "조현우", "신미란", "권태준", "문소영", "양현석", "이지원",
            "박준형", "김서연", "정태우", "안미경", "유재석", "황미나",
            "고동욱", "배수진", "장현우", "천미령", "원준호", "이하늘",
            "강민지", "송태호", "임수진", "박영수", "최민준", "정다운", "한소희"
        ]
        
        for i, name in enumerate(test_names):
            if i < self.MAX_SEATS:
                self.name_entries[i].insert(0, name)

if __name__ == "__main__":
    root = tk.Tk()
    app = LotteryApp(root)
    root.mainloop() 