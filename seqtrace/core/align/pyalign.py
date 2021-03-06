# Copyright (C) 2016 Brian J. Stucky
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


class PairwiseAlignment:
    """
    Provides the ability to calculate an optimal, global, pairwise alignment of two
    DNA sequences.  This is accomplished by an implementation of the Needleman-Wunsch
    pairwise alignment algorithm.
    The default algorithm parameters/assumptions used here are designed for aligning forward
    and reverse sequencing runs.  There are two important things to note.  First, so-called
    "affine gap penalties" are not used.  All gaps are penalized the same, regardless of whether
    they are initial gap openings or extensions.  This is because in interpreting sequencing runs,
    all gaps are mistakes and should be weighted equally.  The exception, of course, are end gaps,
    which are "free".  Second, mismatched bases (or "substitutions", as they are called in the
    literature) are penalized exactly the same as gaps.  The reasoning is the same:  mismatches in
    the alignment, like gaps, do not represent anything biologically real and are all simply
    sequencing mistakes.  Therefore, they should be weighted the same.
    """
    def __init__(self):
        # Define the substitution score matrix.  This matrix includes all IUPAC DNA
        # nucleotide codes.  The scores were generated as follows.  Perfect matches
        # get 6 "points" and complete mismatches get -6 points.  Ambiguous nucleotides
        # are scored as the average score of all possible matches/mismatches. Another
        # way to think of this is that the score for an ambiguous nucleotide will fall
        # between 6 and -6 according to the probability of an exact match.
        # Mathematically, this can be expressed as score = P(exact match) * 12 - 6.
        # Multiplying by 12 simply provides a scaling factor so that most of the scores
        # work out to integer values.
        self.svals = {
'A': {'A':  6, 'T': -6, 'G': -6, 'C': -6, 'W':  0, 'S': -6, 'M':  0, 'K': -6, 'R':  0, 'Y': -6, 'B': -6, 'D': -2, 'H': -2, 'V': -2, 'N': -3},
'T': {'A': -6, 'T':  6, 'G': -6, 'C': -6, 'W':  0, 'S': -6, 'M': -6, 'K':  0, 'R': -6, 'Y':  0, 'B': -2, 'D': -2, 'H': -2, 'V': -6, 'N': -3},
'G': {'A': -6, 'T': -6, 'G':  6, 'C': -6, 'W': -6, 'S':  0, 'M': -6, 'K':  0, 'R':  0, 'Y': -6, 'B': -2, 'D': -2, 'H': -6, 'V': -2, 'N': -3},
'C': {'A': -6, 'T': -6, 'G': -6, 'C':  6, 'W': -6, 'S':  0, 'M':  0, 'K': -6, 'R': -6, 'Y':  0, 'B': -2, 'D': -6, 'H': -2, 'V': -2, 'N': -3},
'W': {'A':  0, 'T':  0, 'G': -6, 'C': -6, 'W':  0, 'S': -6, 'M': -3, 'K': -3, 'R': -3, 'Y': -3, 'B': -4, 'D': -2, 'H': -2, 'V': -4, 'N': -3},
'S': {'A': -6, 'T': -6, 'G':  0, 'C':  0, 'W': -6, 'S':  0, 'M': -3, 'K': -3, 'R': -3, 'Y': -3, 'B': -2, 'D': -4, 'H': -4, 'V': -2, 'N': -3},
'M': {'A':  0, 'T': -6, 'G': -6, 'C':  0, 'W': -3, 'S': -3, 'M':  0, 'K': -6, 'R': -3, 'Y': -3, 'B': -4, 'D': -4, 'H': -2, 'V': -2, 'N': -3},
'K': {'A': -6, 'T':  0, 'G':  0, 'C': -6, 'W': -3, 'S': -3, 'M': -6, 'K':  0, 'R': -3, 'Y': -3, 'B': -2, 'D': -2, 'H': -4, 'V': -4, 'N': -3},
'R': {'A':  0, 'T': -6, 'G':  0, 'C': -6, 'W': -3, 'S': -3, 'M': -3, 'K': -3, 'R':  0, 'Y': -6, 'B': -4, 'D': -2, 'H': -4, 'V': -2, 'N': -3},
'Y': {'A': -6, 'T':  0, 'G': -6, 'C':  0, 'W': -3, 'S': -3, 'M': -3, 'K': -3, 'R': -6, 'Y':  0, 'B': -2, 'D': -4, 'H': -2, 'V': -4, 'N': -3},
'B': {'A': -6, 'T': -2, 'G': -2, 'C': -2, 'W': -4, 'S': -2, 'M': -4, 'K': -2, 'R': -4, 'Y': -2, 'B': -2, 'D': -3, 'H': -3, 'V': -3, 'N': -3},
'D': {'A': -2, 'T': -2, 'G': -2, 'C': -6, 'W': -2, 'S': -4, 'M': -4, 'K': -2, 'R': -2, 'Y': -4, 'B': -3, 'D': -2, 'H': -3, 'V': -3, 'N': -3},
'H': {'A': -2, 'T': -2, 'G': -6, 'C': -2, 'W': -2, 'S': -4, 'M': -2, 'K': -4, 'R': -4, 'Y': -2, 'B': -3, 'D': -3, 'H': -2, 'V': -3, 'N': -3},
'V': {'A': -2, 'T': -6, 'G': -2, 'C': -2, 'W': -4, 'S': -2, 'M': -2, 'K': -4, 'R': -2, 'Y': -4, 'B': -3, 'D': -3, 'H': -3, 'V': -2, 'N': -3},
'N': {'A': -3, 'T': -3, 'G': -3, 'C': -3, 'W': -3, 'S': -3, 'M': -3, 'K': -3, 'R': -3, 'Y': -3, 'B': -3, 'D': -3, 'H': -3, 'V': -3, 'N': -3}
        }

        # The penalty for any gap (except the end gaps) is the same as a base mismatch.
        self.gapp = -6

        self.seq1 = ''
        self.seq2 = ''

        self.seq1aligned = ''
        self.seq2aligned = ''
        self.seq1indexed = []
        self.seq2indexed = []

        self.score = 0

    def setGapPenalty(self, gap_penalty):
        self.gapp = gap_penalty

    def getGapPenalty(self):
        return self.gapp

    def setSequences(self, sequence1, sequence2):
        self.seq1 = sequence1
        self.seq2 = sequence2

    def getSequences(self):
        return (self.seq1, self.seq2)

    def getAlignedSequences(self):
        return (self.seq1aligned, self.seq2aligned)

    def getAlignedSeqIndexes(self):
        return (self.seq1indexed, self.seq2indexed)

    def getAlignmentScore(self):
        return self.score

    def doAlignment(self):
        """ Implements the Needleman-Wunsch pairwise sequence alignment algorithm. """

        seq1len = len(self.seq1)
        seq2len = len(self.seq2)

        # 1st subscript = sequence 1,
        # 2nd subscript = sequence 2
        scores = [ [0 for i in range(seq2len+1)] for j in range(seq1len+1) ]
        tracebk = [ [0 for i in range(seq2len+1)] for j in range(seq1len+1) ]
        
        # initialize the traceback matrix
        for i in range(1, seq1len+1):
            tracebk[i][0] = 'l'
        for j in range(1, seq2len+1):
            tracebk[0][j] = 'u'
        
        # calculate the scores for the alignment matrix and directional
        # pointers for the traceback matrix
        for i in range(1, seq1len+1):
            for j in range(1, seq2len+1):
                # calculate the maximum subscores for this position
                sdiag = scores[i-1][j-1] + self.svals[self.seq1[i-1]][self.seq2[j-1]]
                sup = scores[i][j-1] + self.gapp
                sleft = scores[i-1][j] + self.gapp
                # do not assess a penalty for end gaps
                if j == seq2len:
                    sleft -= self.gapp
                if i == seq1len:
                    sup -= self.gapp
                # record maximum subscore and direction
                if (sdiag >= sup) and (sdiag >= sleft):
                    tracebk[i][j] = 'd'
                    scores[i][j] = sdiag
                elif (sup >= sdiag) and (sup >= sleft):
                    tracebk[i][j] = 'u'
                    scores[i][j] = sup
                else:
                    tracebk[i][j] = 'l'
                    scores[i][j] = sleft

        self.score = scores[seq1len][seq2len]
        
        # follow the directional pointers in the traceback matrix
        # to generate an optimal alignment
        seq1a = list()
        seq2a = list()
        seq1aindex = list()
        seq2aindex = list()
        i = seq1len
        j = seq2len
        while (i > 0) or (j > 0):
            if tracebk[i][j] == 'd':
                seq1a.append(self.seq1[i-1])
                seq2a.append(self.seq2[j-1])
                seq1aindex.append(i-1)
                seq2aindex.append(j-1)
                i -= 1
                j -= 1
            elif tracebk[i][j] == 'u':
                seq1a.append('-')
                seq2a.append(self.seq2[j-1])
                seq1aindex.append(-1)
                seq2aindex.append(j-1)
                j -= 1
            else:
                seq1a.append(self.seq1[i-1])
                seq2a.append('-')
                seq1aindex.append(i-1)
                seq2aindex.append(-1)
                i -= 1
        
        seq1a.reverse()
        seq2a.reverse()
        seq1aindex.reverse()
        seq2aindex.reverse()
        self.seq1aligned = ''.join(seq1a)
        self.seq2aligned = ''.join(seq2a)
        self.seq1indexed = seq1aindex
        self.seq2indexed = seq2aindex

        # go through the sequence indexes and mark the gaps with (-nextbaseindex - 1)
        # so that the index lookups return a more informative value
        seq1gv = seq2gv = -1
        for cnt in range(len(self.seq1indexed)):
            if self.seq1indexed[cnt] == -1:
                self.seq1indexed[cnt] = seq1gv
            else:
                seq1gv -= 1
            if self.seq2indexed[cnt] == -1:
                self.seq2indexed[cnt] = seq2gv
            else:
                seq2gv -= 1

        #print self.seq1indexed

