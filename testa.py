class Solution(object):
    def intersect(self, nums1, nums2):
        """
        :type nums1: List[int]
        :type nums2: List[int]
        :rtype: List[int]
        """
        if len(nums1) > len(nums2):
            unique = set(nums2)
        else:
            unique = set(nums1)
        nums1 = ''.join([str(i) for i in nums1])
        nums2 = ''.join([str(i) for i in nums2])
        ret = []
        for i in unique:
            if nums1.count(str(i)) > 0 and nums1.count(str(i)) > 0:
                ret += [i for k in range(min(nums1.count(str(i)), nums2.count(str(i))))]
        return ret


if __name__ == '__main__':
    s = Solution()
    ret = s.intersect([-2147483648,1,2,3], [1,-2147483648,-2147483648])
    print ret