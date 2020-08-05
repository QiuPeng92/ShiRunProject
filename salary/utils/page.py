class Pagination(object):

    def __init__(self, current_page_num, all_count, request, per_page_num=10, pager_count=11):
        """
        封装分页相关数据
        :param current_page_num: 当前访问页的数字
        :param all_count:    分页数据中的数据总条数
        :param per_page_num: 每页显示的数据条数
        :param pager_count:  最多显示的页码个数
        """
        # 如果current_page_num不是数字,则当前页码赋值为1
        try:
            current_page_num = int(current_page_num)
        except Exception as e:
            current_page_num = 1

        # 如果小于1,则当前页码赋值为1
        if current_page_num < 1:
            current_page_num = 1

        self.current_page_num = current_page_num
        self.all_count = all_count
        self.per_page_num = per_page_num

        # 计算实际总页码(总数除以每页的个数,得出的商+1)
        all_pager, tmp = divmod(all_count, per_page_num)
        # 如果有余数,商加1,整除就直接是商
        if tmp:
            all_pager += 1
        self.all_pager = all_pager
        self.pager_count = pager_count
        # 获取左右页码的数值(左5右5)
        self.pager_count_half = int((pager_count - 1) / 2)  # 5

        # **************保存搜索条件(request.GET是不可更改的)
        import copy
        # 深拷贝(params也是QueryDict,QueryDict不能更改,但是params可以更改,看源码)
        self.params = copy.deepcopy(request.GET)  # {"a":"1","b":"2"}

    @property
    def start(self):
        # 计算初始页码
        return (self.current_page_num - 1) * self.per_page_num

    @property
    def end(self):
        # 计算结束页码
        return self.current_page_num * self.per_page_num

    def page_html(self):
        # 如果总页码 < 11个**********************：
        if self.all_pager <= self.pager_count:
            pager_start = 1
            # 顾头不顾尾,尾巴需要加1
            pager_end = self.all_pager + 1
        # 总页码  > 11***************************
        else:
            # 当前页如果没有左5页
            if self.current_page_num <= self.pager_count_half:
                pager_start = 1
                pager_end = self.pager_count + 1
            # 当前页如果有左5页
            else:
                # (当前页+5如果大于最大页码)
                if (self.current_page_num + self.pager_count_half) > self.all_pager:
                    pager_start = self.all_pager - self.pager_count + 1
                    pager_end = self.all_pager + 1
                # 反之显示左5右5,current_page_num在中间
                else:
                    pager_start = self.current_page_num - self.pager_count_half
                    pager_end = self.current_page_num + self.pager_count_half + 1

        page_html_list = []

        # 首页的li
        # 如果a标签的href直接写?,会根据当前的路径拼接
        self.params["page"] = 1
        first_page = '<li><a href="?%s">首页</a></li>' % (self.params.urlencode())
        page_html_list.append(first_page)

        # 上一页的li
        # 如果当前页码没有上一页
        if self.current_page_num <= 1:
            self.params["page"] = self.current_page_num
            # 则上一页不能点
            prev_page = '<li class="disabled"><a href="#">上一页</a></li>'
            # prev_page = '<li class="disabled"><a href="#">上一页</a></li>'
        else:
            self.params["page"] = self.current_page_num - 1
            # 如果当前页码有上一页
            # prev_page = '<li><a href="?page=%s">上一页</a></li>' % (self.current_page_num - 1,)

            prev_page = '<li><a href="?%s">上一页</a></li>' % (self.params.urlencode())

        page_html_list.append(prev_page)

        # 添加蓝色选中active属性
        for i in range(pager_start, pager_end):
            self.params["page"] = i
            if i == self.current_page_num:
                temp = '<li class="active"><a href="?%s">%s</a></li>' % (self.params.urlencode(), i)
            else:
                temp = '<li><a href="?%s">%s</a></li>' % (self.params.urlencode(), i,)
            page_html_list.append(temp)

        # 下一页的li
        # 判断是否有下一页
        if self.current_page_num >= self.all_pager:
            # 如果没有下一页,就禁用下一页按钮
            next_page = '<li class="disabled"><a href="#">下一页</a></li>'
        else:
            self.params["page"] = self.current_page_num + 1
            next_page = '<li><a href="?%s">下一页</a></li>' % (self.params.urlencode())
        page_html_list.append(next_page)

        # 尾页的li
        self.params["page"] = self.all_pager
        last_page = '<li><a href="?%s">尾页</a></li>' % (self.params.urlencode())
        page_html_list.append(last_page)
        # 将li标签拼接成字符串
        return ''.join(page_html_list)
