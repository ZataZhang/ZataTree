# # updater.py
import json
import hashlib
import os
import shutil
import requests
from pathlib import Path
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--host', default="47.121.123.143", help="服务器IP地址或域名")
args = parser.parse_args()
YOUR_HOST = args.host

class AutoUpdater:
    def __init__(self, config_path=f"http://{YOUR_HOST}/update_config"):
        self.config_path = config_path
        self.config = None
        with open('update.json', 'r', encoding='utf-8') as f:
            self.current_version = json.load(f)['version']
        
    def load_config(self):
        """加载更新配置文件"""
        try:
            # 远程配置文件
            response = requests.get(self.config_path)
            self.config = response.json()
            return True
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
            return False
            
    def check_update(self):
        """检查是否需要更新"""
        if not self.config:
            return False
            
        return self.config['version'] != self.current_version
        
    def calculate_file_hash(self, file_path):
        """计算文件的MD5哈希值"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
        
    def download_update(self, temp_dir="temp_update"):
        """下载更新文件"""
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
        try:
            # 下载更新文件
            update_file = f"{temp_dir}/update.zip"
            download_route = self.config["download_url"]

            
            response = requests.get(f'http://{YOUR_HOST}{download_route}', stream=True)
            with open(update_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            # 验证文件哈希
            if self.calculate_file_hash(update_file) != self.config['file_hash']:
                print("文件验证失败！")
                return False
                
            return update_file
        except Exception as e:
            print(f"下载更新失败: {str(e)}")
            return False
            
    def backup_files(self, backup_dir="backup"):
        """备份当前文件"""
        try:
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # 备份当前目录下的所有文件
            for item in os.listdir('.'):
                if item not in [backup_dir, 'temp_update', 'updater.exe','launcher.exe']:
                    src = os.path.join('.', item)
                    dst = os.path.join(backup_dir, item)
                    if os.path.isfile(src):
                        shutil.copy2(src, dst)
                    elif os.path.isdir(src):
                        shutil.copytree(src, dst)
            return True
        except Exception as e:
            print(f"备份文件失败: {str(e)}")
            return False
            
    def apply_update(self, update_file, temp_dir="temp_update"):
        """应用更新"""
        try:
            # 解压更新文件
            shutil.unpack_archive(update_file, temp_dir)
            
            # 保留指定的旧文件和文件夹
            keep_files = self.config.get('keep_files', [])
            for file in keep_files:
                if os.path.exists(file):
                    # 如果文件在子文件夹中,需要创建对应的临时文件夹
                    temp_path = os.path.join(temp_dir, f"{file}")
                    temp_dir_path = os.path.dirname(temp_path)
                    if temp_dir_path and not os.path.exists(temp_dir_path):
                        os.makedirs(temp_dir_path)
                    print(f"备份: {file} -> {temp_path}")
                    if os.path.isfile(file):
                        shutil.copy2(file, temp_path)
                    elif os.path.isdir(file):
                        # 如果是文件夹则整个复制
                        shutil.copytree(file, temp_path)
            
            need_restart = False
            # 修改删除文件的部分，添加重试和错误处理
            for item in os.listdir('.'):
                if item not in ['backup', 'temp_update', 'updater.exe','launcher.exe']:
                    path = os.path.join('.', item)
                    
                    try:
                        if os.path.isfile(path):
                            try:
                                os.remove(path)
                            except PermissionError:
                                print(f"警告: 文件 {path} 正在使用中，将在重启后更新")
                                need_restart = True
                                continue
                        elif os.path.isdir(path):
                            try:
                                shutil.rmtree(path)
                            except PermissionError:
                                print(f"警告: 目录 {path} 中的某些文件正在使用中，将在重启后更新")
                                need_restart = True
                                continue
                    except Exception as e:
                        print(f"删除 {path} 时出错: {str(e)}")
                        continue
            # 如果需要重启，创建标记文件
            if need_restart:
                with open("need_restart", "w") as f:
                    f.write("1")
                print("部分文件需要在重启后完成更新")
                return True  # 仍然返回True，因为这是预期的行为

            # 复制新文件时添加错误处理
            for item in os.listdir(temp_dir):
                src = os.path.join(temp_dir, item)
                dst = os.path.join('.', item)
                try:
                    if os.path.isfile(src):
                        try:
                            shutil.copy2(src, dst)
                        except PermissionError:
                            print(f"警告: 无法复制文件 {dst}，可能需要重启后完成更新")
                    elif os.path.isdir(src):
                        try:
                            shutil.copytree(src, dst, dirs_exist_ok=True)
                        except PermissionError:
                            print(f"警告: 无法复制目录 {dst}，可能需要重启后完成更新")
                except Exception as e:
                    print(f"复制 {src} 到 {dst} 时出错: {str(e)}")
                    continue
            
            # 恢复需要保留的旧文件和文件夹
            for file in keep_files:
                temp_path = os.path.join(temp_dir, file)
                if os.path.exists(temp_path):
                    # 如果是带路径的文件,先创建目录
                    file_dir = os.path.dirname(file)
                    if file_dir and not os.path.exists(file_dir):
                        os.makedirs(file_dir)
                    if os.path.isfile(temp_path):
                        shutil.copy2(temp_path, file)
                    elif os.path.isdir(temp_path):
                        # 如果是文件夹则整个恢复
                        if os.path.exists(file):
                            shutil.rmtree(file)
                        shutil.copytree(temp_path, file)
            
            return True
        except Exception as e:
            print(f"应用更新失败: {str(e)}, 错误位置: {e.__traceback__.tb_lineno}行")
            return False
    def cleanup(self, temp_dir="temp_update", backup_dir="backup"):
        """清理临时文件和备份"""
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            if os.path.exists("update.zip"):
                os.remove("update.zip")
        except Exception as e:
            print(f"清理文件失败: {str(e)}")

    def update(self):
        """执行更新流程"""
        if not self.load_config():
            return False
            
        if not self.check_update():
            print("当前已是最新版本")
            return True
            
        print(f"发现新版本: {self.config['version']}")
        print("更新说明:")
        print(self.config['publish_notes'])
        
        # 下载更新
        update_file = self.download_update()
        if not update_file:
            return False
        print(f"下载更新文件: {update_file}")
            
        # 备份当前文件
        if not self.backup_files():
            return False
        print("备份完成")
            
        # 应用更新
        if not self.apply_update(update_file):
            print("更新失败，正在恢复备份...")
            if self.apply_update("backup"):
                print("恢复备份成功")
                self.cleanup()
            else:
                print("恢复备份失败，请手动恢复")
            return False
            
        # 清理临时文件和备份
        self.cleanup()
        print(f"更新完成！当前版本: {self.config['version']}")
        return True
    

if __name__ == "__main__":
    try:
        updater = AutoUpdater()
        update_result = updater.update()
        print("更新" + ("成功" if update_result else "失败"))
    except Exception as e:
        print(f"更新过程中发生错误: {str(e)}")
    finally:
        input("按任意键退出...")
