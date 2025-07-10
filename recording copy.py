import streamlit as st
import pickle
import time
import os
import logging
import sys
import io

import func.AmiVoice_recognition as AmiVoice_recognition
from func.function import Functions, Auth

st.set_page_config(
    page_title="音声解析",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 標準出力をリダイレクト
sys.stdout = io.StringIO()
sys.stderr = io.StringIO()

# ログ設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # ロガーのレベルを設定

# ファイルハンドラの設定
file_handler = logging.FileHandler('app.log', mode='a', encoding='utf-8')
file_handler.setLevel(logging.INFO)  # ファイルハンドラのレベルを設定

# フォーマッタの設定
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# ハンドラをロガーに追加
logger.addHandler(file_handler)

# 備考欄をセッション状態と連動させる
def update_remarks():
    st.session_state.remarks = st.session_state.remarks_text


# 環境変数の復号化
functions = Functions()
auth = Auth()

auth.authenticator.login()

if not os.path.exists("save_dir"):
    os.makedirs("save_dir")
# セッション状態の初期化
#-------------------ログインできているときの処理-------------------
if st.session_state['authentication_status']:
    col1, col2, col3 = st.columns([6, 1, 1])
    with col3:
        auth.authenticator.logout()
        
    if 'recognizer' not in st.session_state:
        APP_KEY = functions.AMIVOICE_APP_KEY
        try:
            st.session_state.recognizer = AmiVoice_recognition.SpeechRecognizer(APP_KEY)
            logger.info("AmiVoice認証キーを設定しました")
        except Exception as e:
            logger.error(f"音声認識システムの初期化に失敗しました: {str(e)}")
            st.error(f"音声認識システムの初期化に失敗しました: {str(e)}")
            st.stop()
        st.session_state.is_recording = False
        st.session_state.results = ""
        st.session_state.last_results = ""
        st.session_state.recognition_completed = False
        st.session_state.processing_started = False
        st.session_state.remarks = ""
        st.session_state.realtime_results = ""

    # 備考欄のセッション状態が存在しない場合は初期化
    if 'remarks' not in st.session_state:
        st.session_state.remarks = ""

    #ページの翻訳提案をしないように設定
    st.markdown(
        '<meta name="google" content="notranslate">', 
        unsafe_allow_html=True
    )

    st.title('音声解析アプリケーション')

    #薬剤師リストの読み込み
    pharmacist_list_path = "save_dir/pharmacist_list.pickle"
    if os.path.exists(pharmacist_list_path):
        with open(pharmacist_list_path,"rb") as f:
            pharmacist_list = pickle.load(f)
            pharmacist_list = [name for name in pharmacist_list if name]
    else:
        pharmacist_list = []

    if pharmacist_list:
        user = st.radio(
            "薬剤師を選択",
            pharmacist_list,
            horizontal = True
        )
    else:
        user = st.error("薬剤師リストが存在しません。update pharmacistで薬剤師を登録してください")


    remarks_input = st.text_area(
        "備考欄(検索キー)",
        value=st.session_state.remarks,
        height=68,
        max_chars=200,
        key="remarks_text",
        on_change=update_remarks
    )

    # リアルタイム認識結果を表示するためのプレースホルダー
    realtime_display = st.empty()

    def toggle_recording():
        if not st.session_state.is_recording:
            # 録音開始
            print("録音を開始します")
            try:
                st.session_state.recognizer.clear_results()
                st.session_state.recognizer.start()
                st.session_state.is_recording = True
                st.session_state.results = ""
                st.session_state.realtime_results = ""  # リアルタイム結果をリセット
                st.session_state.recognition_completed = False
                st.session_state.processing_started = False
            except Exception as e:
                logger.error(f"録音開始処理でエラーが発生しました: {e}")
                st.error("録音の開始に失敗しました。")
                st.session_state.is_recording = False
        else:
            # 録音停止
            print("録音を停止します")
            try:
                # 音声認識を停止
                st.session_state.recognizer.stop()
                
                # 結果の取得前に少し待機
                time.sleep(1)
                
                # 結果を取得
                results = st.session_state.recognizer.get_all_results()
                if results:
                    st.session_state.results = results
                    st.session_state.last_results = results
                    st.session_state.recognition_completed = st.session_state.recognizer.is_recognition_completed()
                    st.session_state.processing_started = True
                else:
                    st.warning("認識結果が取得できませんでした。")
                
                st.session_state.is_recording = False
                
            except Exception as e:
                logger.error(f"録音停止処理でエラーが発生しました: {e}")
                st.error("録音の停止に失敗しました。")
                st.session_state.is_recording = False
                st.session_state.recognition_completed = False
                st.session_state.processing_started = False
                # エラーが発生した場合でも、音声認識を確実に停止
                try:
                    st.session_state.recognizer.stop()
                except:
                    pass

    # 録音状態の表示
    status_text = st.empty()
    if st.session_state.is_recording:
        status_text.info("録音中... マイクに向かって話しかけてください\n録音は10秒未満ではうまく認識されない場合があります")
    else:
        status_text.info("録音を開始するにはボタンを押してください")

    # 録音ボタン
    button_text = "録音停止" if st.session_state.is_recording else "録音開始"
    if st.button(button_text, on_click=toggle_recording):
        pass

    # 録音ボタンの後に認識結果の表示を追加
    if st.session_state.is_recording:
        try:
            current_results = st.session_state.recognizer.get_all_results()
            if current_results != st.session_state.realtime_results:
                st.session_state.realtime_results = current_results
                logger.debug(f"認識結果を更新: {current_results}")
        except Exception as e:
            logger.error(f"認識結果の取得中にエラーが発生しました: {e}")

        if st.session_state.realtime_results:
            realtime_display.warning(st.session_state.realtime_results)
        else:
            realtime_display.warning("認識中...")
        
        # 画面を更新
        time.sleep(2)
        st.rerun()

    place1 = st.empty()

    if st.session_state.processing_started and st.session_state.recognition_completed:
        if st.session_state.last_results != "":
            place1.warning("音声認識が完了しました。要約中です。")
            f = Functions()
            recognition_text = st.session_state.last_results
            summary = f.make_summary(recognition_text)
            f.append_pickle_files(user, "now", st.session_state.remarks, recognition_text, summary)
            st.session_state.processing_started = False
            st.session_state.recognition_completed = False
            st.session_state.results = ""
            st.session_state.last_results = ""
            st.session_state.remarks = ""  # 備考欄を空にする
            place1.warning("要約が完了しデータを保存しました。")
        else:
            place1.warning("認識結果のテキストが存在しません。\n録音が短すぎる可能性があります。")

#-------------------ログインできていない場合-------------------

elif st.session_state["authentication_status"] is False:
    st.error("ユーザー名またはパスワードが正しくありません")
elif st.session_state["authentication_status"] is None:
    st.warning("ユーザー名とパスワードを入力しログインしてください")