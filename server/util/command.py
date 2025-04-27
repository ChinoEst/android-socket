import logging
import subprocess



def run_command(work_path, env, code):
    try:
        logging.info(f"執行命令: {code}")
        
        command = f"conda run -n {env} python {code}"
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            cwd=work_path,
            text=True,
            capture_output=True
        )
        
        logging.info(f"執行結果: {result.stdout}")
        return result.stdout

    except subprocess.CalledProcessError as e:
        logging.error(f"命令執行失敗: {e.stderr}")
        raise
