"""Помощник для написания песен."""

import sys
import os

# Fix path for frozen executables
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    os.chdir(application_path)
    if application_path not in sys.path:
        sys.path.insert(0, application_path)

import streamlit as st
import webbrowser

sys.path.insert(0, os.path.dirname(__file__))

from engine import rhymes

from engine import structure

from engine import editor

from utils import export

from engine import syllable_counter

from engine import history

from engine import phrases


# Local aliases for show_phrases convenience
PHRASE_CATEGORIES = phrases.PHRASES

st.set_page_config(page_title="Помощник для написания песен", page_icon="🎵", layout="wide")

# Auto-open browser when running as standalone exe
if getattr(sys, 'frozen', False):
    import threading
    def open_browser():
        try:
            import time
            time.sleep(3)
            webbrowser.open("http://localhost:8501")
        except Exception:
            pass
    threading.Thread(target=open_browser, daemon=True).start()


# Initialize session state early
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"
if "search_word" not in st.session_state:
    st.session_state.search_word = ""
if "song_title" not in st.session_state:
    st.session_state.song_title = None
if "selected_template" not in st.session_state:
    st.session_state.selected_template = None
if "current_song" not in st.session_state:
    st.session_state.current_song = None
if "temp_context" not in st.session_state:
    st.session_state.temp_context = None
if "show_export" not in st.session_state:
    st.session_state.show_export = False
if "rhyme_results" not in st.session_state:
    st.session_state.rhyme_results = []

css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")

if os.path.exists(css_path):

    with open(css_path) as f:

        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# =============================================================================

# Helper Functions

# =============================================================================



def feature_card(icon, title, description, page_key):

    """Возвращает HTML для карточки функции."""

    return f'''

    <div class="feature-card" style="cursor:pointer;">

        <span class="feature-icon">{icon}</span>

        <div class="feature-title">{title}</div>

        <div class="feature-desc">{description}</div>

    </div>

    '''



def styled_button(label, key, use_container_width=True):

    return st.button(label, key=key, use_container_width=use_container_width)



def stat_card(value, label):

    return f'''<div style="background:#16213e; border:1px solid #2a2a4a; border-radius:12px; padding:1.5rem; text-align:center; width:100%;">
        <div style="color:#e94560; font-size:2rem; font-weight:700; margin-bottom:0.25rem;">{value}</div>
        <div style="color:#b8b8d4; font-size:0.875rem;">{label}</div>
    </div>'''



def song_card(song):

    style_name = song.get('style_id', 'N/A').upper()

    created = song.get('created_at', 'N/A')[:16].replace('T', ' ')

    return f'''<div style="background:#16213e; border:1px solid #2a2a4a; border-radius:16px; padding:2rem; margin:1rem 0; display:flex; flex-direction:column;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
            <h3 style="margin:0; color:#ffffff; font-size:1.25rem;">{song['title']}</h3>
            <span style="background:linear-gradient(135deg, #e94560, #0f3460); color:white; padding:0.25rem 0.75rem; border-radius:20px; font-size:0.8rem; font-weight:600;">{style_name}</span>
        </div>
        <div style="color:#b8b8d4; font-size:0.85rem; margin-bottom:1rem;">📅 Создано: {created}</div>
    </div>'''

# =============================================================================

# Navigation

# =============================================================================



NAV_ITEMS = [

    ("🏠 Главная", "home"),

    ("🔤 Рифмы", "rhymes"),

    ("📋 Шаблоны", "templates"),

    ("✍️ Редактор", "editor"),

    ("📚 Фразы", "phrases"),

    ("🎶 Мои песни", "songs"),

]



if "current_page" not in st.session_state:

    st.session_state.current_page = "home"

# Sidebar navigation

with st.sidebar:

    st.markdown("### 🎵 Помощник")

    for label, pk in NAV_ITEMS:

        if st.button(

            label,

            key=f"nav_{pk}",

            use_container_width=True,

            type="primary" if st.session_state.current_page == pk else "secondary",

        ):

            st.session_state.current_page = pk

            st.rerun()

    st.markdown('<hr style="border-color:var(--border-color);">', unsafe_allow_html=True)
def show_home():
    """Главная страница с карточками функций и популярными словами."""
    st.markdown('<h1 class="gradient-text" style="text-align:center;margin-bottom:0.5rem;font-weight:800;">Помощник для написания песен</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:var(--text-secondary);font-size:1.1rem;margin-bottom:2rem;">Создавайте музыку вместе с AI — рифмы, шаблоны, редактор</p>', unsafe_allow_html=True)

    # Feature cards
    st.markdown('<h3 style="color:var(--text-primary);margin-bottom:1rem;">✨ Возможности</h3>', unsafe_allow_html=True)
    features = [
        ("🔤", "Поиск рифм", "Находите рифмы к любому слову по окончанию или точно", "rhymes"),
        ("📋", "Шаблоны песен", "Выбирайте готовые структуры для разных жанров", "templates"),
        ("✍️", "Редактор", "Пишите текст песен с подсказками и советами", "editor"),
    ]
    col1, col2, col3 = st.columns(3)
    cards = [
        f'<div class="card-container" style="text-align:center;padding:2rem;height:100%;display:flex;flex-direction:column;justify-content:center;">'
        f'<span style="font-size:3rem;margin-bottom:1rem;display:block;">{icon}</span>'
        f'<h4 style="color:var(--text-primary);margin:0 0 0.5rem 0;font-weight:600;">{title}</h4>'
        f'<p style="color:var(--text-secondary);font-size:0.9rem;margin:0;line-height:1.5;">{desc}</p></div>'
        for icon, title, desc, _ in features
    ]
    with col1:
        st.markdown(cards[0], unsafe_allow_html=True)
    with col2:
        st.markdown(cards[1], unsafe_allow_html=True)
    with col3:
        st.markdown(cards[2], unsafe_allow_html=True)

    # Open pages directly
    st.markdown("")
    nav_cols = st.columns(3)
    for i, (_, _, _, pk) in enumerate(features):
        with nav_cols[i]:
            btn_label = f"Открыть {pk.capitalize()}"
            if st.button(btn_label, key=f"open_{pk}", use_container_width=True):
                st.session_state.current_page = pk
                st.rerun()

    # Popular words section
    st.markdown('<h3 style="color:var(--text-primary);margin-top:2rem;">🔥 Популярные слова</h3>', unsafe_allow_html=True)
    popular = rhymes.get_common_rhymes()
    num_cols = min(5, len(popular))
    cols = st.columns(num_cols)
    for i, word in enumerate(popular):
        with cols[i % num_cols]:
            if styled_button(f"🎯 {word.capitalize()}", f"pop_{word}", use_container_width=True):
                st.session_state.current_page = "rhymes"
                st.session_state.search_word = word
                st.rerun()

    # Stats
    st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)
    all_songs = editor.get_all_songs()
    total_songs = len(all_songs)
    styles_count = len(structure.get_available_styles())
    stats_cols = st.columns(3)
    with stats_cols[0]:
        st.markdown(stat_card(total_songs, "Песен создано"), unsafe_allow_html=True)
    with stats_cols[1]:
        st.markdown(stat_card(styles_count, "Жанров"), unsafe_allow_html=True)
    with stats_cols[2]:
        st.markdown(stat_card(len(popular), "Слов в словаре"), unsafe_allow_html=True)
# =============================================================================
# show_rhymes
# =============================================================================

def show_rhymes():
    """Страница поиска рифм."""
    st.markdown('<h2 style="color:var(--text-primary);">🔤 Поиск рифм</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:var(--text-secondary);margin-bottom:1.5rem;">Введите слово или окончание для поиска рифм</p>', unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["🔍 По слову", "✨ По окончанию", "📊 Популярные"])

    with tab1:
        search_word = st.text_input("Введите слово:", value=st.session_state.get("search_word", ""), placeholder="например: любовь, свет, ночь...", label_visibility="collapsed")
        max_res = st.slider("Максимум результатов:", 5, 50, 10)
        if styled_button("🔎 Найти рифмы", "search_rhyme"):
            if search_word.strip():
                result = rhymes.get_rhymes(search_word.strip(), max_results=max_res)
                if result:
                    st.markdown(f'<p style="color:var(--accent-primary);font-weight:600;">Рифмы к слову "{search_word.strip().capitalize()}":</p>', unsafe_allow_html=True)
                    num_cols = min(3, len(result))
                    cols = st.columns(num_cols)
                    for i, rhyme in enumerate(result):
                        with cols[i % num_cols]:
                            st.markdown(
                                f'<div class="card-container" style="text-align:center;padding:1rem;">'
                                f'<span style="font-size:1.5rem;">💡</span><br><strong style="color:var(--text-primary);font-size:1.1rem;">{rhyme.capitalize()}</strong></div>',
                                unsafe_allow_html=True,
                            )
                    st.session_state.rhyme_results = result
                else:
                    st.warning(f"😔 Рифмы к слову «{search_word.strip()}» не найдены. Попробуйте другое слово.")
                    st.session_state.rhyme_results = []
            else:
                st.info("💬 Введите слово для поиска рифм.")
                st.session_state.rhyme_results = []

    with tab2:
        ending = st.text_input("Введите окончание:", placeholder="-ция, -сть, -ть...", label_visibility="collapsed")
        min_len = st.slider("Мин. длина слова:", 1, 10, 2)
        max_res_2 = st.slider("Максимум результатов:", 5, 50, 15)
        if styled_button("🔎 Найти по окончанию", "search_ending"):
            if ending.strip():
                result = rhymes.get_rhymes_by_ending(ending.strip(), min_length=min_len, max_results=max_res_2)
                if result:
                    st.markdown(f'<p style="color:var(--accent-primary);font-weight:600;">Слова с окончанием "{ending.strip()}":</p>', unsafe_allow_html=True)
                    cols = st.columns(4)
                    for i, word in enumerate(result):
                        with cols[i % 4]:
                            st.markdown(
                                f'<div class="card-container" style="text-align:center;padding:0.8rem;">'
                                f'<span style="color:var(--accent-primary);">📝</span><br><strong style="color:var(--text-primary);">{word.capitalize()}</strong></div>',
                                unsafe_allow_html=True,
                            )
                else:
                    st.warning(f"😔 Слова с окончанием «{ending.strip()}» не найдены.")
            else:
                st.info("💬 Введите окончание для поиска.")

    with tab3:
        st.markdown('<p style="color:var(--text-secondary);">Самые популярные слова для рифмовки</p>', unsafe_allow_html=True)
        popular = rhymes.get_common_rhymes()
        cols = st.columns(5)
        for i, word in enumerate(popular):
            with cols[i % 5]:
                rhyme_count = len(rhymes.get_rhymes(word))
                if styled_button(f"🎯 {word.capitalize()}\n({rhyme_count} рифм)", f"pop_rhyme_{word}", use_container_width=True):
                    st.session_state.current_page = "rhymes"
                    st.session_state.search_word = word
                    st.rerun()
# =============================================================================
# show_templates
# =============================================================================

def show_templates():
    """Страница выбора шаблонов песен — все ячейки одинаковой высоты."""
    st.markdown('<h2 style="color:var(--text-primary);">📋 Шаблоны песен</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:var(--text-secondary);margin-bottom:1.5rem;">Выберите жанр для создания песни</p>', unsafe_allow_html=True)

    styles = structure.get_available_styles()
    icons = {"поп": "🎤", "рок": "🎸", "рэп": "🎙️", "баллада": "🎻", "инди": "🌿", "шансон": "🎩"}

    # Единый HTML-контейнер flex — гарантирует одинаковую высоту
    st.markdown(
        '<style>'
        '.tmpl-container{display:flex;flex-wrap:wrap;gap:1rem;align-items:stretch;margin-bottom:1rem;}'
        '.tmpl-item{flex:1 1 280px;min-width:250px;}'
        '.tmpl-inner{display:flex;flex-direction:column;height:100%;}'
        '</style>',
        unsafe_allow_html=True,
    )

    num_cols = 3
    for i in range(0, len(styles), num_cols):
        batch = styles[i:i + num_cols]
        
        # HTML-контейнер для строки карточек одинаковой высоты
        st.markdown('<div class="tmpl-container">', unsafe_allow_html=True)
        
        for style in batch:
            icon = icons.get(style["id"], "🎵")
            st.markdown(
                f'<div class="tmpl-item">'
                f'<div class="tmpl-inner" style="background:var(--bg-card);border:1px solid var(--border-color);border-radius:16px;padding:1.5rem;">'
                f'<div style="flex-grow:1;">'
                f'<div style="font-size:2.5rem;margin-bottom:0.5rem;">{icon}</div>'
                f'<h4 style="color:var(--text-primary);margin:0.25rem 0 0.5rem 0;font-weight:600;">{style["name"]}</h4>'
                f'<p style="color:var(--text-secondary);font-size:0.85rem;margin:0;line-height:1.5;">{style["description"]}</p>'
                f'</div>'
                f'<div style="margin-top:auto;"></div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Кнопки после каждой строки
        for style in batch:
            if st.button(f"Выбрать {style['name']}", key=f"sel_{style['id']}", use_container_width=True):
                st.session_state.current_page = "editor"
                st.session_state.selected_template = style["id"]
                st.rerun()
        st.markdown("")
# =============================================================================
# show_editor
# =============================================================================

def show_editor():
    """Редактор текста песни."""
    st.markdown('<h2 style="color:var(--text-primary);">✍️ Редактор песен</h2>', unsafe_allow_html=True)

    # Step 1: Select template
    if "selected_template" not in st.session_state or st.session_state.selected_template is None:
        selected = st.selectbox("Выберите жанр:", [s["id"] for s in structure.get_available_styles()],
                                format_func=lambda x: dict([(s["id"], f"{s['name']}") for s in structure.get_available_styles()])[x])
        if styled_button("Далее →", "tmpl_next"):
            st.session_state.selected_template = selected
            st.rerun()
        return

    style_id = st.session_state.selected_template
    template = structure.get_template(style_id)
    if not template:
        st.error("Шаблон не найден.")
        return

    st.markdown(f'<div class="card-container" style="margin-bottom:1.5rem;">'
                f'<span style="font-size:2rem;">🎵</span> <strong style="color:var(--text-primary);">{template["name"]}</strong>'
                f'<p style="color:var(--text-secondary);">{template["description"]}</p></div>', unsafe_allow_html=True)

    # Step 2: Song title
    if "song_title" not in st.session_state or st.session_state.song_title is None:
        title = st.text_input("Название песни:", placeholder="Введите название...",
                              value=st.session_state.get("song_title", ""), label_visibility="collapsed")
        if styled_button("Создать песню ✨", "create_song"):
            if title.strip():
                st.session_state.song_title = title.strip()
                st.session_state.temp_context = structure.create_template_context(style_id)
                st.rerun()
            else:
                st.warning("Введите название песни.")
        return

    # Step 3: Section editors
    song_title = st.session_state.song_title
    temp_ctx = st.session_state.temp_context

    # Если temp_ctx пустой (открыли существующую песню) — создаём его
    if temp_ctx is None or "sections" not in temp_ctx:
        temp_ctx = structure.create_template_context(style_id)
        st.session_state.temp_context = temp_ctx

    st.markdown(f'<h3 style="color:var(--accent-primary);">{song_title}</h3>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:var(--text-secondary);margin-bottom:1.5rem;">Жанр: {template["name"]}</p>', unsafe_allow_html=True)

    sections = temp_ctx["sections"]
    total_secs = temp_ctx["total_sections"]

    # Если песня уже загружена из файла — синхронизируем текст из current_song
    if "current_song" in st.session_state and st.session_state.current_song:
        saved_song = st.session_state.current_song
        saved_sections = saved_song.get("sections", {})
        for sec_key in sections:
            if sec_key in saved_sections:
                sections[sec_key]["text"] = saved_sections[sec_key].get("text", "")
                sections[sec_key]["tips"] = saved_sections[sec_key].get("tips", [])
                sections[sec_key]["lines_hint"] = saved_sections[sec_key].get("lines_hint", 0)

    # Progress bar
    filled = sum(1 for s in sections.values() if s.get("text", "").strip())
    progress = filled / total_secs if total_secs > 0 else 0
    st.progress(progress)
    st.markdown(f'<p style="text-align:center;color:var(--text-secondary);">Заполнено: {filled}/{total_secs} секций</p>', unsafe_allow_html=True)
    st.markdown("")

    # Insert phrase into section
    if "phrase_to_insert" in st.session_state:
        phrase = st.session_state.phrase_to_insert
        st.markdown(
            f'<div class="card-container" style="border-color:var(--accent-primary);">'
            f'<p style="color:var(--accent-primary);font-weight:600;margin:0;">📝 Фраза готова к вставке:</p>'
            f'<p style="color:var(--text-secondary);font-style:italic;margin:0.5rem 0;">{phrase}</p>'
            f'</div>', unsafe_allow_html=True
        )
        insert_section = st.selectbox(
            "Вставить в секцию:",
            list(sections.keys()),
            format_func=lambda k: sections[k]["label"],
            key="insert_into_section"
        )
        col_ins1, col_ins2 = st.columns(2)
        with col_ins1:
            if st.button("✅ Вставить", key="confirm_insert", use_container_width=True):
                if insert_section:
                    current = sections[insert_section].get("text", "")
                    if current.strip():
                        sections[insert_section]["text"] = current + "\n" + phrase
                    else:
                        sections[insert_section]["text"] = phrase
                    sections[insert_section]["text"] = sections[insert_section]["text"].strip() + "\n"
                    temp_ctx["sections"] = sections
                    st.success("Фраза вставлена!")
                del st.session_state.phrase_to_insert
                st.rerun()
        with col_ins2:
            if st.button("❌ Отмена", key="cancel_insert", use_container_width=True):
                del st.session_state.phrase_to_insert
                st.rerun()

        st.markdown("---")

    for sec_key, sec_data in sections.items():
        sec_label = sec_data["label"]
        sec_type = sec_data["type"]
        type_icons = {"куплет": "🎤", "припев": "🔊", "бридж": "🌉", "интро": "🎬", "проигрыш": "🎸", "аутро": "🏁"}
        icon = type_icons.get(sec_type, "📝")
        lines_hint = sec_data.get("lines_hint", 0)

        with st.expander(f"{icon} {sec_label}", expanded=False):
            current_text = sec_data.get("text", "")
            
            # Верхняя строка: тип, подсказки и текстовое поле
            col_text, col_info = st.columns([4, 1])
            
            with col_text:
                new_text = st.text_area(
                    "Текст:", value=current_text, height=150,
                    placeholder=f"Введите текст {sec_label.lower()}...",
                    label_visibility="collapsed",
                    key=f"section_{sec_key}",
                )
                
                # Отображение слогов
                if new_text.strip():
                    lines = [l for l in new_text.split("\n") if l.strip()]
                    syllable_stats = []
                    for line in lines:
                        syllables = syllable_counter.count_line_syllables(line)
                        syllable_stats.append(syllables)
                    
                    if syllable_stats:
                        avg_syllables = sum(syllable_stats) / len(syllable_stats)
                        
                        # Визуальный индикатор отклонения от заданного размера
                        rhythm_color = "var(--success-color)"  # зелёный
                        rhythm_icon = "✅"
                        if lines_hint > 0:
                            deviation = abs(avg_syllables - lines_hint)
                            if deviation > 2:
                                rhythm_color = "var(--accent-primary)"  # красный
                                rhythm_icon = "⚠️"
                            elif deviation > 1:
                                rhythm_color = "var(--warning-color)"  # жёлтый
                                rhythm_icon = "⚡"
                        
                        st.markdown(
                            f'<div style="display:flex;gap:1rem;margin-top:0.5rem;flex-wrap:wrap;">'
                            f'<span style="color:var(--accent-primary);font-weight:600;">📏 {avg_syllables:.1f} слогов/строку</span>'
                            f'<span style="color:var(--text-secondary);">• {len(lines)} строк</span>'
                            f'<span style="color:{rhythm_color};font-weight:600;">{rhythm_icon} {rhythm_icon == "✅" and "Ритм в норме" or "Отклонение от нормы"}</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
            
            with col_info:
                st.markdown(f"**Тип:** {sec_type.capitalize()}")
                if lines_hint > 0:
                    st.markdown(f"**Строк:** ~{lines_hint}")
                
                if sec_data.get("tips"):
                    st.markdown("---")
                    st.markdown("**💡 Советы:**")
                    for tip in sec_data["tips"][:3]:
                        st.caption(tip)
                
                # Подсказки рифмов
                if new_text.strip():
                    lines = [l for l in new_text.split("\n") if l.strip()]
                    last_line = lines[-1] if lines else ""
                    if last_line.strip():
                        words = last_line.lower().split()
                        if words:
                            last_word = words[-1].strip('.,!?;:")\']')
                            if last_word:
                                suggested_rhymes = rhymes.get_rhymes(last_word, max_results=5)
                                if suggested_rhymes:
                                    st.markdown("---")
                                    st.markdown("**🎵 Рифмы:**")
                                    for rhyme in suggested_rhymes[:5]:
                                        if st.button(f"🔤 {rhyme.capitalize()}", use_container_width=True, type="secondary", key=f"rhyme_btn_{sec_key}_{rhyme}"):
                                            # Insert rhyme into current line
                                            if last_line.strip():
                                                current_lines = [l for l in new_text.split("\n") if l.strip()]
                                                if current_lines:
                                                    current_lines[-1] = last_line.rstrip() + " " + rhyme
                                                    sections[sec_key]["text"] = "\n".join(current_lines).strip()
                                                    temp_ctx["sections"] = sections
                                                    st.success(f"Рифма '{rhyme}' добавлена!")
                                                    st.rerun()

            if new_text != current_text:
                sections[sec_key]["text"] = new_text
                temp_ctx["sections"] = sections

            if lines_hint > 0:
                text_lines = [l for l in new_text.split("\n") if l.strip()] if new_text.strip() else []
                progress = min(1.0, len(text_lines) / lines_hint) if lines_hint > 0 else 0
                st.caption(f"Строк: {len(text_lines)} / {lines_hint}")
                st.progress(progress)

    st.markdown("")

    # Action buttons
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        if styled_button("💾 Сохранить", "save_song"):
            song = editor.create_song(song_title, style_id, temp_ctx)
            st.session_state.current_song = song
            st.success(f"✅ Песня «{song_title}» создана! ID: {song['id']}")
            st.rerun()
    with col_b:
        if styled_button("💾 Сохранить версию", "save_version"):
            if "current_song" in st.session_state:
                song = st.session_state.current_song
                version = history.save_version(song["id"], song, "Ручное сохранение")
                st.session_state.show_versions = True
                st.success(f"✅ Версия {version['version']} сохранена!")
                st.rerun()
    with col_c:
        if styled_button("📤 Экспорт", "export_song"):
            if "current_song" in st.session_state:
                song = st.session_state.current_song
                fmt = st.radio("Формат:", ["TXT", "PDF"], key="exp_fmt", label_visibility="collapsed")
                if fmt == "TXT":
                    txt = export.export_to_txt(song)
                    st.download_button("📥 Скачать TXT", data=txt, file_name=f"{song_title}.txt", mime="text/plain")
                else:
                    try:
                        pdf_bytes = export.export_to_pdf(song)
                        st.download_button("📥 Скачать PDF", data=pdf_bytes, file_name=f"{song_title}.pdf", mime="application/pdf")
                    except Exception as e:
                        st.error(f"Ошибка: {e}")
    with col_d:
        if styled_button("🗑️ Удалить", "del_editor"):
            if "current_song" in st.session_state:
                editor.delete_song(st.session_state.current_song["id"])
                del st.session_state.current_song
                for k in list(st.session_state.keys()):
                    if k.startswith("section_"):
                        del st.session_state[k]
                st.session_state.song_title = None
                st.session_state.selected_template = None
                st.rerun()

    # If song exists, show stats
    if "current_song" in st.session_state and st.session_state.current_song:
        st.markdown("<hr>", unsafe_allow_html=True)
        song = st.session_state.current_song
        stats = editor.get_song_stats(song)
        st.markdown('<h4 style="color:var(--text-primary);">📊 Статистика</h4>', unsafe_allow_html=True)
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown(stat_card(stats["total_lines"], "Всего строк"), unsafe_allow_html=True)
        with sc2:
            st.markdown(stat_card(stats["rhymed_lines"], "Рифмованных"), unsafe_allow_html=True)
        with sc3:
            pct = (stats["rhymed_lines"] / stats["total_lines"] * 100) if stats["total_lines"] > 0 else 0
            st.markdown(stat_card(f"{pct:.0f}%", "Рифма %"), unsafe_allow_html=True)
        
        # История версий
        if "current_song" in st.session_state:
            song = st.session_state.current_song
            versions = history.get_version_summary(song["id"])
            
            if versions:
                st.markdown('<h4 style="color:var(--text-primary);margin-top:1.5rem;">📜 История версий</h4>', unsafe_allow_html=True)
                
                for v in versions:
                    with st.container():
                        st.markdown(
                            f'<div style="background:var(--bg-card);border:1px solid var(--border-color);border-radius:12px;padding:1rem;margin-bottom:0.5rem;display:flex;justify-content:space-between;align-items:center;">'
                            f'<div>'
                            f'<span style="color:var(--accent-primary);font-weight:600;">v{v["version"]}</span> '
                            f'<span style="color:var(--text-secondary);font-size:0.85rem;">{v["date"]} {v["time"]}</span>'
                            f'{v["comment"] and " — " + v["comment"] or ""}'
                            f'</div>'
                            f'<div>'
                            f'<span style="color:var(--text-secondary);font-size:0.85rem;">{v["sections"]} секций</span>'
                            f' • '
                            f'<span style="color:var(--text-secondary);font-size:0.85rem;">{v["lines"]} строк</span>'
                            f' • '
                            f'<span style="color:var(--success-color);font-size:0.85rem;">{v["progress"]:.0f}%</span>'
                            f'</div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                        
                        col_v1, col_v2 = st.columns(2)
                        with col_v1:
                            if st.button(f"🔄 Восстановить v{v['version']}", key=f"restore_v{v['version']}", use_container_width=True, type="secondary"):
                                restored = history.restore_version(song["id"], v["version"])
                                if restored:
                                    st.session_state.current_song = restored
                                    st.session_state.temp_context = structure.create_template_context(song.get("style_id", "поп"))
                                    st.success(f"✅ Восстановлена версия {v['version']}!")
                                    st.rerun()
                        with col_v2:
                            if v["version"] < versions[-1]["version"]:
                                if st.button(f"🔍 Сравнить", key=f"compare_v{v['version']}", use_container_width=True, type="secondary"):
                                    st.session_state.compare_version = v["version"]
                                    st.rerun()
# =============================================================================
# show_songs
# =============================================================================

def show_songs():
    """Страница списка сохранённых песен."""
    st.markdown('<h2 style="color:var(--text-primary);">🎶 Мои песни</h2>', unsafe_allow_html=True)

    songs = editor.get_all_songs()
    if not songs:
        st.markdown('<div class="card-container" style="text-align:center;">'
                    '<span style="font-size:3rem;">🎵</span><br>'
                    '<p style="color:var(--text-secondary);">Пока нет сохранённых песен. Создайте первую!</p>'
                    '</div>', unsafe_allow_html=True)
        if styled_button("Создать песню ✨", "go_create"):
            st.session_state.current_page = "templates"
            st.rerun()
        return

    for song in songs:
        with st.container():
            st.markdown(song_card(song), unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                if styled_button("📖 Открыть", f"open_{song['id']}"):
                    st.session_state.current_page = "editor"
                    st.session_state.current_song = editor.load_song(song["id"])
                    st.session_state.song_title = song.get("title", "Без названия")
                    st.session_state.selected_template = song.get("style_id", "поп")
                    st.rerun()
            with col2:
                if styled_button("📤 Экспорт", f"exp_{song['id']}"):
                    st.session_state.current_page = "editor"
                    st.session_state.current_song = editor.load_song(song["id"])
                    st.session_state.show_export = True
                    st.session_state.song_title = song.get("title", "Без названия")
                    st.session_state.selected_template = song.get("style_id", "поп")
                    st.rerun()
            with col3:
                if styled_button("🗑️ Удалить", f"del_{song['id']}"):
                    editor.delete_song(song["id"])
                    st.success("Песня удалена.")

# =============================================================================
# show_phrases
# =============================================================================

def show_phrases():
    """Страница библиотеки фраз и метафор — использует engine/phrases.py."""
    st.markdown('<h2 style="color:var(--text-primary);">📚 Фразы и метафоры</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:var(--text-secondary);margin-bottom:1.5rem;">Готовые выражения для ваших песен</p>', unsafe_allow_html=True)

    # Tabs: Browse by category / Search / Random
    tab1, tab2, tab3 = st.tabs(["📂 Категории", "🔍 Поиск", "🎲 Случайные"])

    with tab1:
        cat_icons = {
            "love": "💕", "nature": "🌿", "pain": "💔",
            "hope": "🌟", "dreams": "💭", "time": "⏰",
        }
        cat_labels = {
            "love": "Любовь", "nature": "Природа", "pain": "Боль",
            "hope": "Надежда", "dreams": "Мечты", "time": "Время",
        }
        selected_cat = st.selectbox(
            "Выберите категорию:",
            list(PHRASE_CATEGORIES.keys()),
            format_func=lambda x: f"{cat_icons.get(x, '📝')} {cat_labels.get(x, x)}",
            key="phrase_category"
        )
        if selected_cat:
            cat_phrases = PHRASE_CATEGORIES[selected_cat]
            st.markdown(
                f'<h3 style="color:var(--text-primary);margin:1rem 0;">'
                f'{cat_icons.get(selected_cat, "")} {cat_labels.get(selected_cat, selected_cat)}</h3>',
                unsafe_allow_html=True
            )
            cols = st.columns(2)
            for i, phrase in enumerate(cat_phrases):
                with cols[i % 2]:
                    st.markdown(
                        f'<div class="card-container" style="padding:1.2rem;margin-bottom:0.5rem;">'
                        f'<p style="color:var(--text-secondary);margin:0;font-style:italic;">{phrase}</p>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    if st.button("📋 Копировать", key=f"copy_{selected_cat}_{i}", use_container_width=True, type="secondary"):
                        st.session_state.copied_phrase = phrase
                        st.success("Скопировано!")

    with tab2:
        keyword = st.text_input("Введите ключевое слово:", placeholder="например: любовь, время, звезда...", key="phrase_search_input")
        if keyword and keyword.strip():
            results = phrases.search_phrases(keyword.strip())
            if results:
                st.markdown(f'**Найдено {len(results)} фраз:**')
                for r in results:
                    st.markdown(
                        f'<div class="card-container" style="padding:1rem;">'
                        f'<p style="color:var(--text-secondary);margin:0;font-style:italic;">{r["phrase"]}</p>'
                        f'<span style="font-size:0.8rem;color:var(--text-muted);">({r["category"]})</span>'
                        f'</div>', unsafe_allow_html=True
                    )
            else:
                st.info("Ничего не найдено. Попробуйте другое слово.")

    with tab3:
        count = st.slider("Количество:", 1, 10, 3)
        rand_cat = st.selectbox("Категория (необязательно):", ["Все"] + list(PHRASE_CATEGORIES.keys()), key="phrase_rand_cat")
        if st.button("🎲 Получить случайные фразы", "get_random_phrases"):
            selected = None if rand_cat == "Все" else rand_cat
            random_phrases = phrases.get_random_phrases(count=count, category=selected)
            if random_phrases:
                cols = st.columns(min(2, len(random_phrases)))
                for i, p in enumerate(random_phrases):
                    with cols[i % 2]:
                        st.markdown(
                            f'<div class="card-container" style="padding:1.2rem;">'
                            f'<p style="color:var(--text-secondary);margin:0;font-style:italic;">{p}</p>'
                            f'</div>', unsafe_allow_html=True
                        )
            else:
                st.warning("Нет фраз в выбранной категории.")

    # Global: insert copied phrase into editor
    st.markdown("")
    if "copied_phrase" in st.session_state:
        st.markdown(
            f'<div class="card-container" style="margin-top:1rem;">'
            f'<p style="color:var(--text-primary);font-size:1.1rem;font-style:italic;">{st.session_state.copied_phrase}</p>'
            f'<p style="color:var(--text-secondary);font-size:0.85rem;">(нажмите Ctrl+C чтобы скопировать)</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if st.button("📝 Вставить в редактор", key="insert_phrase", use_container_width=True):
            st.session_state.phrase_to_insert = st.session_state.copied_phrase
            st.session_state.current_page = "editor"
            st.rerun()

# =============================================================================
# Main routing
# =============================================================================

PAGE_FUNCTIONS = {
    "home": show_home,
    "rhymes": show_rhymes,
    "templates": show_templates,
    "editor": show_editor,
    "phrases": show_phrases,
    "songs": show_songs,
}

# Show current page
current_page = st.session_state.current_page
if current_page in PAGE_FUNCTIONS:
    PAGE_FUNCTIONS[current_page]()
else:
    show_home()
