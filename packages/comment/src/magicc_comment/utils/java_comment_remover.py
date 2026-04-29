# magicc_comment/utils/java_comment_remover.py
import re

class JavaCommentRemover:
    """Java 注释删除器"""
    
    @staticmethod
    def remove(content: str) -> str:
        """删除 Java 文件中的所有注释"""
        result = []
        i = 0
        in_string = False
        in_char = False
        
        while i < len(content):
            ch = content[i]
            
            # 处理字符串和字符字面量
            if not in_string and not in_char and ch == '"':
                in_string = True
                result.append(ch)
                i += 1
                continue
            elif not in_string and not in_char and ch == "'":
                in_char = True
                result.append(ch)
                i += 1
                continue
            elif in_string and ch == '"' and (i == 0 or content[i-1] != '\\'):
                in_string = False
                result.append(ch)
                i += 1
                continue
            elif in_char and ch == "'" and (i == 0 or content[i-1] != '\\'):
                in_char = False
                result.append(ch)
                i += 1
                continue
            
            # 不在字符串内，处理注释
            if not in_string and not in_char:
                # 单行注释 //
                if ch == '/' and i + 1 < len(content) and content[i+1] == '/':
                    while i < len(content) and content[i] != '\n':
                        i += 1
                    result.append('\n')
                    i += 1
                    continue
                # 多行注释 /* */
                elif ch == '/' and i + 1 < len(content) and content[i+1] == '*':
                    i += 2
                    while i + 1 < len(content) and not (content[i] == '*' and content[i+1] == '/'):
                        i += 1
                    i += 2
                    continue
                else:
                    result.append(ch)
                    i += 1
            else:
                result.append(ch)
                i += 1
        
        cleaned = ''.join(result)
        # 清理多余空行
        cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)
        return cleaned