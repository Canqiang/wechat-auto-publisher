
import re
from typing import Dict, List
import jieba
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class ContentOptimizer:
    """内容优化服务"""
    
    def __init__(self):
        self.load_sensitive_words()
        self.load_seo_keywords()
    
    def load_sensitive_words(self):
        """加载敏感词库"""
        try:
            with open('data/sensitive_words.txt', 'r', encoding='utf-8') as f:
                self.sensitive_words = set(line.strip() for line in f if line.strip())
            logger.info(f"加载敏感词库: {len(self.sensitive_words)}个词汇")
        except FileNotFoundError:
            logger.warning("敏感词库文件不存在，使用默认敏感词")
            self.sensitive_words = {'违法', '诈骗', '赌博', '暴力', '血腥'}
        except Exception as e:
            logger.error(f"加载敏感词库失败: {str(e)}")
            self.sensitive_words = set()
    
    def load_seo_keywords(self):
        """加载SEO关键词"""
        self.seo_keywords = {
            'tech': ['人工智能', 'AI', '科技', '创新', '数字化'],
            'health': ['健康', '养生', '运动', '饮食', '医疗'],
            'finance': ['投资', '理财', '金融', '股票', '基金'],
            'lifestyle': ['生活', '时尚', '旅游', '美食', '文化']
        }
    
    def optimize_content(self, content: str, category: str = None) -> Dict:
        """优化文章内容"""
        result = {
            'optimized_content': content,
            'suggestions': [],
            'seo_score': 0,
            'readability_score': 0
        }
        
        # 1. 敏感词检测和替换
        content = self.filter_sensitive_words(content)
        
        # 2. SEO优化
        seo_result = self.optimize_for_seo(content, category)
        result['optimized_content'] = seo_result['content']
        result['seo_score'] = seo_result['score']
        
        # 3. 可读性优化
        readability = self.improve_readability(result['optimized_content'])
        result['optimized_content'] = readability['content']
        result['readability_score'] = readability['score']
        
        # 4. 添加互动元素
        result['optimized_content'] = self.add_engagement_elements(
            result['optimized_content']
        )
        
        # 5. 生成摘要
        result['summary'] = self.generate_summary(result['optimized_content'])
        
        return result
    
    def filter_sensitive_words(self, content: str) -> str:
        """过滤敏感词"""
        for word in self.sensitive_words:
            if word in content:
                content = content.replace(word, '*' * len(word))
                logger.warning(f"发现敏感词: {word}")
        return content
    
    def optimize_for_seo(self, content: str, category: str) -> Dict:
        """SEO优化"""
        result = {'content': content, 'score': 0}
        
        if category and category in self.seo_keywords:
            keywords = self.seo_keywords[category]
            
            # 计算关键词密度
            word_count = len(content)
            keyword_count = sum(content.count(kw) for kw in keywords)
            density = keyword_count / word_count * 100
            
            # 优化关键词密度（目标2-3%）
            if density < 2:
                # 在适当位置插入关键词
                for keyword in keywords[:3]:
                    if content.count(keyword) < 3:
                        # 在段落开头或结尾添加关键词
                        paragraphs = content.split('\n\n')
                        if paragraphs:
                            paragraphs[0] = f"{keyword}是当今的热门话题。{paragraphs[0]}"
                            paragraphs[-1] = f"{paragraphs[-1]}关注{keyword}，获取更多精彩内容。"
                            result['content'] = '\n\n'.join(paragraphs)
            
            result['score'] = min(100, density * 33)
        
        return result
    
    def improve_readability(self, content: str) -> Dict:
        """提高可读性"""
        result = {'content': content, 'score': 0}
        
        # 1. 分段优化
        paragraphs = content.split('\n\n')
        optimized_paragraphs = []
        
        for para in paragraphs:
            # 段落不要太长
            if len(para) > 500:
                # 在合适的标点处分段
                sentences = re.split(r'[。！？]', para)
                new_para = []
                current = []
                current_len = 0
                
                for sent in sentences:
                    if current_len + len(sent) > 250:
                        optimized_paragraphs.append('。'.join(current) + '。')
                        current = [sent]
                        current_len = len(sent)
                    else:
                        current.append(sent)
                        current_len += len(sent)
                
                if current:
                    optimized_paragraphs.append('。'.join(current) + '。')
            else:
                optimized_paragraphs.append(para)
        
        # 2. 添加小标题
        if len(optimized_paragraphs) > 5:
            # 每3-4段添加一个小标题
            with_headers = []
            for i, para in enumerate(optimized_paragraphs):
                if i > 0 and i % 3 == 0:
                    # 根据内容生成小标题
                    header = self._generate_subheading(para)
                    with_headers.append(f"\n## {header}\n")
                with_headers.append(para)
            
            result['content'] = '\n\n'.join(with_headers)
        else:
            result['content'] = '\n\n'.join(optimized_paragraphs)
        
        # 计算可读性分数
        avg_sentence_length = len(content) / max(1, content.count('。'))
        result['score'] = min(100, 100 - abs(avg_sentence_length - 30))
        
        return result
    
    def add_engagement_elements(self, content: str) -> str:
        """添加互动元素"""
        # 在文章开头添加引导语
        intro = "👋 亲爱的读者，今天为您带来精彩内容！\n\n"
        
        # 在文章结尾添加互动引导
        outro = "\n\n💬 觉得文章有帮助吗？欢迎点赞、评论和分享！\n关注我们，获取更多优质内容～"
        
        # 添加思考问题
        questions = [
            "\n\n🤔 思考：这个观点您认同吗？",
            "\n\n💡 小贴士：记得实践这些方法哦！",
            "\n\n📝 笔记：这个知识点值得记录下来"
        ]
        
        # 在适当位置插入互动元素
        paragraphs = content.split('\n\n')
        if len(paragraphs) > 3:
            # 在中间位置插入一个思考问题
            mid = len(paragraphs) // 2
            paragraphs[mid] += questions[0]
        
        return intro + '\n\n'.join(paragraphs) + outro
    
    def generate_summary(self, content: str, max_length: int = 100) -> str:
        """生成文章摘要"""
        # 提取前几句话作为摘要
        sentences = re.split(r'[。！？]', content)
        summary = []
        current_length = 0
        
        for sent in sentences:
            if current_length + len(sent) > max_length:
                break
            summary.append(sent)
            current_length += len(sent)
        
        return '。'.join(summary) + '。' if summary else content[:max_length]
    
    def _generate_subheading(self, paragraph: str) -> str:
        """根据段落内容生成小标题"""
        # 使用jieba分词
        words = jieba.cut(paragraph)
        word_freq = Counter(words)
        
        # 过滤停用词
        stop_words = {'的', '是', '在', '和', '了', '有', '我', '你', '他', '她', '它'}
        for word in stop_words:
            word_freq.pop(word, None)
        
        # 获取高频词
        top_words = word_freq.most_common(3)
        if top_words:
            return ''.join([word for word, _ in top_words[:2]])
        
        return "精彩内容"
    
    def check_content_quality(self, content: str) -> Dict:
        """检查内容质量"""
        quality_score = 100
        issues = []
        recommendations = []
        
        # 1. 长度检查
        length = len(content)
        if length < 300:
            quality_score -= 20
            issues.append("内容过短")
            recommendations.append("建议增加内容深度，至少300字")
        elif length > 5000:
            quality_score -= 10
            issues.append("内容过长")
            recommendations.append("建议精简内容或分为多篇文章")
        
        # 2. 段落结构检查
        paragraphs = content.split('\n\n')
        if len(paragraphs) < 3:
            quality_score -= 15
            issues.append("段落过少")
            recommendations.append("建议增加段落分隔，提升可读性")
        
        # 3. 句子长度检查
        sentences = re.split(r'[。！？]', content)
        long_sentences = [s for s in sentences if len(s) > 100]
        if len(long_sentences) > len(sentences) * 0.3:
            quality_score -= 10
            issues.append("长句过多")
            recommendations.append("建议拆分长句，提升阅读流畅度")
        
        # 4. 重复内容检查
        words = jieba.cut(content)
        word_freq = Counter(words)
        most_common = word_freq.most_common(10)
        for word, freq in most_common:
            if len(word) > 1 and freq > length // 100:  # 词频过高
                quality_score -= 5
                issues.append(f"'{word}'词频过高")
                recommendations.append(f"减少'{word}'的使用频率，增加表达多样性")
        
        # 5. 标点符号检查
        punctuation_count = len(re.findall(r'[。！？，、；：]', content))
        if punctuation_count < length // 50:
            quality_score -= 10
            issues.append("标点符号过少")
            recommendations.append("适当增加标点符号，提升阅读节奏")
        
        return {
            'quality_score': max(0, quality_score),
            'issues': issues,
            'recommendations': recommendations,
            'word_count': length,
            'paragraph_count': len(paragraphs),
            'sentence_count': len(sentences)
        }
    
    def enhance_readability(self, content: str) -> Dict:
        """提升内容可读性"""
        enhanced_content = content
        improvements = []
        
        # 1. 添加表情符号
        enhanced_content = self._add_emojis(enhanced_content)
        improvements.append("添加了相关表情符号")
        
        # 2. 优化段落结构
        enhanced_content = self._optimize_paragraphs(enhanced_content)
        improvements.append("优化了段落结构")
        
        # 3. 添加强调格式
        enhanced_content = self._add_emphasis(enhanced_content)
        improvements.append("添加了文本强调")
        
        # 4. 插入阅读提示
        enhanced_content = self._add_reading_hints(enhanced_content)
        improvements.append("插入了阅读提示")
        
        return {
            'enhanced_content': enhanced_content,
            'improvements': improvements,
            'readability_score': self._calculate_readability_score(enhanced_content)
        }
    
    def _add_emojis(self, content: str) -> str:
        """添加相关表情符号"""
        emoji_map = {
            '重要': '⚠️',
            '注意': '⚠️',
            '提醒': '💡',
            '建议': '💡',
            '技巧': '💡',
            '方法': '🔧',
            '步骤': '📝',
            '总结': '📋',
            '结论': '✅',
            '成功': '✅',
            '失败': '❌',
            '问题': '❓',
            '疑问': '❓',
            '思考': '🤔',
            '分析': '📊',
            '数据': '📊',
            '趋势': '📈',
            '增长': '📈',
            '下降': '📉',
            '时间': '⏰',
            '金钱': '💰',
            '投资': '💰',
            '学习': '📚',
            '教育': '📚',
            '健康': '🏥',
            '运动': '🏃',
            '食物': '🍎',
            '科技': '💻',
            '未来': '🚀'
        }
        
        for keyword, emoji in emoji_map.items():
            if keyword in content and emoji not in content:
                # 在关键词前添加表情符号，但不要过多
                content = content.replace(keyword, f"{emoji} {keyword}", 1)
        
        return content
    
    def _optimize_paragraphs(self, content: str) -> str:
        """优化段落结构"""
        paragraphs = content.split('\n\n')
        optimized = []
        
        for para in paragraphs:
            # 如果段落太长，尝试分割
            if len(para) > 400:
                sentences = re.split(r'([。！？])', para)
                current_para = ""
                
                for i in range(0, len(sentences), 2):
                    if i + 1 < len(sentences):
                        sentence = sentences[i] + sentences[i + 1]
                        if len(current_para + sentence) > 200 and current_para:
                            optimized.append(current_para.strip())
                            current_para = sentence
                        else:
                            current_para += sentence
                
                if current_para:
                    optimized.append(current_para.strip())
            else:
                optimized.append(para)
        
        return '\n\n'.join(optimized)
    
    def _add_emphasis(self, content: str) -> str:
        """添加文本强调"""
        # 为重要概念添加加粗
        important_patterns = [
            r'(第[一二三四五六七八九十]\w*)',
            r'(\d+[个月年天小时分钟])',
            r'([0-9]+%)',
            r'(关键是|重点是|核心是)',
            r'(总结|结论|要点)'
        ]
        
        for pattern in important_patterns:
            content = re.sub(pattern, r'**\1**', content)
        
        return content
    
    def _add_reading_hints(self, content: str) -> str:
        """添加阅读提示"""
        hints = [
            "\n\n💡 **小贴士**: 以下内容比较重要，建议仔细阅读。\n\n",
            "\n\n📝 **划重点**: 这里的信息值得记录下来。\n\n",
            "\n\n🤔 **思考一下**: 这个观点您怎么看？\n\n"
        ]
        
        paragraphs = content.split('\n\n')
        if len(paragraphs) > 4:
            # 在中间位置插入提示
            mid = len(paragraphs) // 2
            paragraphs.insert(mid, hints[0])
        
        return '\n\n'.join(paragraphs)
    
    def _calculate_readability_score(self, content: str) -> int:
        """计算可读性分数"""
        score = 50  # 基础分
        
        # 段落数量
        paragraphs = len(content.split('\n\n'))
        if 3 <= paragraphs <= 8:
            score += 10
        
        # 平均句子长度
        sentences = re.split(r'[。！？]', content)
        if sentences:
            avg_sentence_length = len(content) / len(sentences)
            if 15 <= avg_sentence_length <= 35:
                score += 10
        
        # 表情符号使用
        emoji_count = len(re.findall(r'[🎯💡📝🤔📊📈📉⏰💰📚🏥🏃🍎💻🚀⚠️✅❌❓]', content))
        if emoji_count > 0:
            score += min(emoji_count * 2, 15)
        
        # 强调文本
        emphasis_count = len(re.findall(r'\*\*.*?\*\*', content))
        if emphasis_count > 0:
            score += min(emphasis_count * 3, 15)
        
        return min(100, score)
    
    def generate_tags(self, content: str, max_tags: int = 10) -> List[str]:
        """自动生成内容标签"""
        # 使用jieba提取关键词
        words = jieba.cut(content)
        word_freq = Counter(words)
        
        # 过滤停用词和短词
        stop_words = {
            '的', '是', '在', '和', '了', '有', '我', '你', '他', '她', '它',
            '这', '那', '与', '及', '或', '但', '而', '就', '都', '很',
            '也', '还', '只', '又', '把', '被', '让', '从', '到', '为',
            '一个', '一些', '这个', '那个', '可以', '应该', '需要', '能够'
        }
        
        # 提取候选标签
        candidate_tags = []
        for word, freq in word_freq.items():
            if (len(word) >= 2 and 
                word not in stop_words and 
                not word.isdigit() and
                freq >= 2):
                candidate_tags.append((word, freq))
        
        # 排序并返回前N个
        candidate_tags.sort(key=lambda x: x[1], reverse=True)
        tags = [tag for tag, _ in candidate_tags[:max_tags]]
        
        # 如果标签不够，添加一些通用标签
        if len(tags) < 3:
            generic_tags = ['实用技巧', '生活指南', '干货分享', '经验总结']
            for tag in generic_tags:
                if tag not in tags:
                    tags.append(tag)
                    if len(tags) >= max_tags:
                        break
        
        return tags
    
    def optimize_for_platform(self, content: str, platform: str = 'wechat') -> Dict:
        """针对特定平台优化内容"""
        if platform == 'wechat':
            return self._optimize_for_wechat(content)
        elif platform == 'weibo':
            return self._optimize_for_weibo(content)
        elif platform == 'zhihu':
            return self._optimize_for_zhihu(content)
        else:
            return {'optimized_content': content, 'changes': []}
    
    def _optimize_for_wechat(self, content: str) -> Dict:
        """微信公众号内容优化"""
        optimized = content
        changes = []
        
        # 1. 添加引导关注
        if '关注' not in optimized:
            optimized += "\n\n🔔 觉得内容有用？别忘了点赞和关注我们！"
            changes.append("添加了关注引导")
        
        # 2. 添加互动元素
        if '评论' not in optimized:
            optimized += "\n\n💬 在评论区分享你的看法吧～"
            changes.append("添加了评论互动")
        
        # 3. 控制长度
        if len(optimized) > 4000:
            # 如果太长，添加"点击阅读原文"提示
            optimized = optimized[:3500] + "...\n\n👉 点击阅读原文查看完整内容"
            changes.append("添加了阅读原文引导")
        
        return {
            'optimized_content': optimized,
            'changes': changes,
            'platform_score': self._calculate_platform_score(optimized, 'wechat')
        }
    
    def _optimize_for_weibo(self, content: str) -> Dict:
        """微博内容优化"""
        optimized = content
        changes = []
        
        # 微博有字数限制
        if len(optimized) > 2000:
            optimized = optimized[:1900] + "...展开全文"
            changes.append("适配微博字数限制")
        
        # 添加话题标签
        tags = self.generate_tags(content, 3)
        if tags:
            hashtags = ' '.join([f"#{tag}#" for tag in tags[:2]])
            optimized = f"{optimized}\n\n{hashtags}"
            changes.append("添加了话题标签")
        
        return {
            'optimized_content': optimized,
            'changes': changes,
            'platform_score': self._calculate_platform_score(optimized, 'weibo')
        }
    
    def _optimize_for_zhihu(self, content: str) -> Dict:
        """知乎内容优化"""
        optimized = content
        changes = []
        
        # 知乎更注重深度和专业性
        if len(optimized) < 800:
            optimized += "\n\n---\n\n**扩展阅读建议**：\n1. 深入了解相关理论\n2. 查看更多实践案例\n3. 关注行业最新动态"
            changes.append("添加了扩展阅读建议")
        
        # 添加数据支撑
        if '数据' not in optimized and '统计' not in optimized:
            optimized += "\n\n📊 **相关数据**：建议补充权威数据支撑观点"
            changes.append("提醒添加数据支撑")
        
        return {
            'optimized_content': optimized,
            'changes': changes,
            'platform_score': self._calculate_platform_score(optimized, 'zhihu')
        }
    
    def _calculate_platform_score(self, content: str, platform: str) -> int:
        """计算平台适配分数"""
        score = 50
        
        if platform == 'wechat':
            # 微信公众号评分标准
            if '关注' in content: score += 10
            if '点赞' in content: score += 10
            if '评论' in content: score += 10
            if 500 <= len(content) <= 3000: score += 20
            
        elif platform == 'weibo':
            # 微博评分标准
            if '#' in content: score += 15  # 话题标签
            if len(content) <= 2000: score += 20  # 字数适中
            if '转发' in content: score += 10
            
        elif platform == 'zhihu':
            # 知乎评分标准
            if len(content) >= 800: score += 20  # 内容深度
            if '数据' in content or '研究' in content: score += 15
            if '参考' in content or '来源' in content: score += 10
        
        return min(100, score)