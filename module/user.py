import uiautomation as auto
import threading
import time
import logging
import os
from wcferry import Wcf

class WeChatManager:
    def __init__(self, debug=False, language='zh'):
        from dotenv import load_dotenv
        load_dotenv(dotenv_path='./../config/.env')
        self.target_chatroom = os.getenv('TARGET_GROUP')
        self.lock = threading.Lock()
        self.UiaAPI: auto.WindowControl = auto.WindowControl(ClassName='WeChatMainWndForPC', searchDepth=1)
        self.set_debug(debug)
        self.language = language
        self.LOG = logging.getLogger('WCM')
        time_now = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        logging.basicConfig(level=logging.INFO, filename='./logs/wechatbot-agent-'+time_now+'.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.LOG.info('WeChatManager started')
        self._show()
        MainControl1 = [i for i in self.UiaAPI.GetChildren() if not i.ClassName][0]
        MainControl2 = MainControl1.GetFirstChildControl()
        self.NavigationBox, self.SessionBox, self.ChatBox = MainControl2.GetChildren()

        self.window = auto.WindowControl(searchDepth=1, ClassName='WeChatMainWndForPC', Name='微信')
        self.window.SetActive()

        self.wcf = Wcf(debug=True)

        self.invition_queue = []
        self.daemon_invition = threading.Thread(target=self._daemon_invition, daemon=True)
        self.daemon_invition.start()
        

    def set_debug(self, debug):
        self.debug = debug
    def _show(self):
        pass
    def set_default(self):
        self.window.SetActive()
        self.NavigationBox.ButtonControl(Name='聊天').Click()
        self.LOG.info("set default")
    def get_all_children(self, control):
        for i in control.GetChildren():
            print(i.Name, i.ClassName)
            self.get_all_children(i)
    def _daemon_invition(self):
        while True:
            self.wcf.get_contacts()
            # check if the user is both in the contact list and in the invition queue
            # use list comprehension to get the intersection
            # if the user is in the queue, send group invition
            for x in self.wcf.contacts:
                # x is a dict
                if x['name'] in self.invition_queue:
                    self.wcf.add_chatroom_members('47780907741@chatroom', x['wxid'])
                    self.invition_queue.remove(x['name'])
            time.sleep(10)
    # based on ui automation, really slow
    # each time we can only do one thing, we need a lock
    # 0: user not found
    # 1: sent friend request
    # 2: already friend
    def send_friend_request(self, id: str, score: int = 0):
        with self.lock:
            self.set_default()
            self.NavigationBox.ButtonControl(Name='通讯录').Click()
            self.SessionBox.ButtonControl(Name='添加朋友').Click(simulateMove=False)
            self.SessionBox.EditControl(Name='微信号/手机号').Click(simulateMove=False)
            self.SessionBox.EditControl(Name='微信号/手机号').SendKeys(id)
            self.SessionBox.TextControl(Name=f'搜索：{id}').Click(simulateMove=False)
            ContactProfileWnd = auto.PaneControl(ClassName='ContactProfileWnd')
            if ContactProfileWnd.Exists(maxSearchSeconds=2):
                name = ContactProfileWnd.TextControl().Name
                print(name)
                send = ContactProfileWnd.ButtonControl(Name='添加到通讯录')
                if send.Exists(maxSearchSeconds=1):
                    
                    send.Click(simulateMove=False)
                    NewFriendsWnd = self.UiaAPI.WindowControl(ClassName='WeUIDialog')
                    msgedit = NewFriendsWnd.TextControl(Name="发送添加朋友申请").GetParentControl().EditControl()
                    msgedit.Click(simulateMove=False)
                    msgedit.SendKeys('{Ctrl}a', waitTime=0)
                    msgedit.SendKeys('您好，您的测试得分为%d分，欢迎加入 Linux 俱乐部！' % score)
                    NewFriendsWnd.ButtonControl(Name='确定').Click(simulateMove=False)
                    return [1, name]
                else:
                    return [2, name]
                
            else:
                return [0,'']
    # 0: user not found
    # 1: sent friend request, add to queue and wait for response
    # 2: already friend, send group invition
    # 3: already in group
    def send_group_invition(self, id: str, score: int = 0):
        [status, name] = self.send_friend_request(id, score)
        if status == 0:
            return 0
        self.invition_queue.append(name)
        return 1
    
    def busy_block(self):
        while True:
            time.sleep(1)
    def enableReceivingMsg(self) -> None:
        def innerProcessMsg(wcf: Wcf):
            while wcf.is_receiving_msg():
                try:
                    msg = wcf.get_msg()
                    self.LOG.info(msg)
                except Exception as e:
                    if(e == None):
                        continue
        self.wcf.enable_receiving_msg()
        threading.Thread(target=innerProcessMsg, name="GetMessage", args=(self.wcf,), daemon=True).start()